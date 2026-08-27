"""Controlled scaling experiment for LEVI's structured episodic memory.

This is deliberately an *offline retrieval* experiment.  It does not make
model/API calls: downstream_success is a replay proxy (whether the required
memory appeared in the context window), not a claim about end-to-end agent
success.  Use ``evaluate_agent.py`` separately once a task-domain replay is
available.

Examples:
    python evals/run_memory_scaling.py
    python evals/run_memory_scaling.py --sizes 10 50 200 1000 --seeds 0 1 2
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).parent.parent))

from levi.memory import EpisodicMemory
from levi.schema import EpisodicRecord, Outcome


EVALS_DIR = Path(__file__).parent
BENCHMARK_PATH = EVALS_DIR / "benchmark_dataset.json"
ANCHOR_PATH = EVALS_DIR / "mock_memory.jsonl"

# Nearby operational tasks intentionally share vocabulary with the anchors.
DISTRACTOR_TEMPLATES = [
    ("Restart Redis service after a connection timeout", ["redis", "connection", "linux"]),
    ("List temporary log files in /tmp", ["linux", "filesystem", "tmp"]),
    ("Find a large archive under /tmp", ["linux", "filesystem", "tmp"]),
    ("Create a PostgreSQL database and user", ["postgresql", "database", "linux"]),
    ("Check Docker container network connectivity", ["docker", "networking", "connection"]),
    ("Write a Python cleanup script in /tmp", ["python", "script", "filesystem", "tmp"]),
]


def load_anchors() -> list[EpisodicRecord]:
    """Load the fixed relevant records used by the existing benchmark."""
    return EpisodicMemory(str(ANCHOR_PATH)).all()


def make_distractor(index: int, density: str, duplicate_rate: float, rng: random.Random) -> EpisodicRecord:
    task, tags = DISTRACTOR_TEMPLATES[index % len(DISTRACTOR_TEMPLATES)]
    if density == "low":
        task = f"Archive project note {index} for later review"
        tags = ["archive", "notes"]
    elif density == "medium":
        task = f"{task} (run {index})"
    else:  # high: preserve the same lexical features, making score ties likely
        task = f"{task} {index}"

    if rng.random() < duplicate_rate:
        task = task.rsplit(" ", 1)[0]

    # Later timestamps model memories that arrived after the validated anchors.
    return EpisodicRecord(
        id=f"noise_{index:06d}",
        task=task,
        plan=["Inspect the environment", "Apply the documented procedure"],
        actions=[],
        outcome=Outcome.SUCCESS,
        verifier_notes="Synthetic distractor for controlled retrieval evaluation.",
        tags=tags,
        timestamp=(datetime(2030, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=index)).isoformat(),
        source="scaling_eval",
    )


def deduplicate(records: Iterable[EpisodicRecord]) -> list[EpisodicRecord]:
    """Keep one record per normalized task/tags signature, retaining oldest."""
    kept: dict[tuple[str, tuple[str, ...]], EpisodicRecord] = {}
    for record in records:
        key = (record.task.lower(), tuple(sorted(tag.lower() for tag in record.tags)))
        if key not in kept or record.timestamp < kept[key].timestamp:
            kept[key] = record
    return list(kept.values())


def build_pool(size: int, density: str, duplicate_rate: float, seed: int, policy: str) -> list[EpisodicRecord]:
    anchors = load_anchors()
    if size < len(anchors):
        raise ValueError(f"Pool size must be at least {len(anchors)} (the anchor count).")
    rng = random.Random(seed)
    pool = anchors + [make_distractor(i, density, duplicate_rate, rng) for i in range(size - len(anchors))]
    if policy == "dedup":
        pool = deduplicate(pool)
    if policy == "prune":
        # A transparent fixed-cap policy: remove redundant noise before retrieval.
        pool = anchors + deduplicate(pool[len(anchors):])[: max(0, size // 2 - len(anchors))]
    return pool


def metric_summary(memory: EpisodicMemory, benchmark: list[dict], k: int, threshold: float) -> dict[str, float]:
    recalls: list[float] = []
    precisions: list[float] = []
    reciprocal_ranks: list[float] = []
    no_match: list[float] = []
    inspected = 0
    replay_hits = 0

    for example in benchmark:
        retrieved = memory.retrieve(example["query"], k=k, threshold=threshold)
        retrieved_ids = [record.id for record in retrieved]
        truth = set(example["ground_truth_memories"])
        inspected += len(retrieved)
        if not truth:
            no_match.append(float(not retrieved_ids))
            continue
        hits = sum(record_id in truth for record_id in retrieved_ids)
        recalls.append(hits / len(truth))
        precisions.append(hits / len(retrieved_ids) if retrieved_ids else 0.0)
        rank = next((i + 1 for i, record_id in enumerate(retrieved_ids) if record_id in truth), None)
        reciprocal_ranks.append(1.0 / rank if rank else 0.0)
        replay_hits += int(hits > 0)

    count = len(recalls)
    return {
        "recall_at_k": sum(recalls) / count,
        "precision_at_k": sum(precisions) / count,
        "mrr": sum(reciprocal_ranks) / count,
        "no_match_accuracy": sum(no_match) / len(no_match) if no_match else 0.0,
        "context_records": inspected / len(benchmark),
        # Explicitly a retrieval-to-context proxy, not an LLM task-success score.
        "replay_context_success": replay_hits / count,
    }


def run_condition(size: int, density: str, duplicate_rate: float, seed: int, policy: str, k: int, threshold: float, benchmark: list[dict]) -> dict[str, object]:
    pool = build_pool(size, density, duplicate_rate, seed, policy)
    with tempfile.TemporaryDirectory(prefix="levi_scaling_") as directory:
        path = Path(directory) / "pool.jsonl"
        memory = EpisodicMemory(str(path))
        for record in pool:
            memory.write(record)
        metrics = metric_summary(memory, benchmark, k, threshold)
    return {
        "requested_pool_size": size,
        "actual_pool_size": len(pool),
        "distractor_density": density,
        "duplicate_rate": duplicate_rate,
        "seed": seed,
        "policy": policy,
        "k": k,
        "threshold": threshold,
        **metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LEVI vectorless memory scaling conditions.")
    parser.add_argument("--sizes", type=int, nargs="+", default=[10, 50, 200, 1_000])
    parser.add_argument("--densities", choices=["low", "medium", "high"], nargs="+", default=["low", "medium", "high"])
    parser.add_argument("--duplicate-rates", type=float, nargs="+", default=[0.0, 0.3])
    parser.add_argument("--policies", choices=["baseline", "threshold", "dedup", "prune"], nargs="+", default=["baseline", "threshold", "dedup", "prune"])
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--output", type=Path, default=EVALS_DIR / "memory_scaling_results.csv")
    args = parser.parse_args()

    with BENCHMARK_PATH.open() as handle:
        benchmark = json.load(handle)
    if not ANCHOR_PATH.exists():
        raise SystemExit("Missing evals/mock_memory.jsonl. Run evals/generate_mock_memory.py first.")

    results: list[dict[str, object]] = []
    for size in args.sizes:
        for density in args.densities:
            for duplicate_rate in args.duplicate_rates:
                for policy in args.policies:
                    # Threshold is an ablation, not a magic optimum; report it plainly.
                    threshold = 4.0 if policy == "threshold" else 2.0
                    for seed in args.seeds:
                        results.append(run_condition(size, density, duplicate_rate, seed, policy, args.k, threshold, benchmark))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)

    print(f"Wrote {len(results)} conditions to {args.output}")
    for row in results:
        if row["distractor_density"] == "high" and row["duplicate_rate"] == 0.3 and row["seed"] == 0:
            print("size={requested_pool_size:>5} policy={policy:<9} recall={recall_at_k:.3f} mrr={mrr:.3f} replay={replay_context_success:.3f}".format(**row))


if __name__ == "__main__":
    main()


