"""
Episodic memory store.

V0 rule: vectorless. Retrieval here is exact/structured (tags, task
substring, outcome, recency) — not similarity search. This is intentional:
we want to find out how far structured retrieval gets us before reaching
for embeddings (see project notes, Section 8/9).

Storage: append-only JSONL file. Simple, inspectable, greppable.
Swap this for a real DB later without changing the interface.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .schema import EpisodicRecord, Outcome


class EpisodicMemory:
    def __init__(self, path: str = "episodic_memory.jsonl"):
        self.path = Path(path)
        self.path.touch(exist_ok=True)

    def write(self, record: EpisodicRecord) -> None:
        with self.path.open("a") as f:
            f.write(json.dumps(record.to_dict()) + "\n")

    def all(self) -> list[EpisodicRecord]:
        records = []
        with self.path.open("r") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(EpisodicRecord.from_dict(json.loads(line)))
        return records

    # --- structured retrieval (no embeddings) ---

    def by_outcome(self, outcome: Outcome) -> list[EpisodicRecord]:
        return [r for r in self.all() if r.outcome == outcome]

    def by_tag(self, tag: str) -> list[EpisodicRecord]:
        return [r for r in self.all() if tag in r.tags]

    def search_task(self, substring: str) -> list[EpisodicRecord]:
        substring = substring.lower()
        return [r for r in self.all() if substring in r.task.lower()]

    def recent(self, n: int = 5) -> list[EpisodicRecord]:
        return sorted(self.all(), key=lambda r: r.timestamp, reverse=True)[:n]

    def stats(self) -> dict:
        records = self.all()
        if not records:
            return {"total": 0}
        outcomes = {}
        for r in records:
            outcomes[r.outcome.value] = outcomes.get(r.outcome.value, 0) + 1
        return {"total": len(records), "by_outcome": outcomes}