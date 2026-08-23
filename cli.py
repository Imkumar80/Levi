"""
Quick demo / manual test of the V0 loop.

Usage:
    python -m levi.cli "12 * (3 + 4)"
    python -m levi.cli "remember to check episodic stats" --stats
"""

from __future__ import annotations

import argparse
import json
import os

from .agent import LeviAgent
from .memory import EpisodicMemory
from .planner import MockPlanner
from .tools import registry


def build_agent(memory_path: str = "episodic_memory.jsonl") -> LeviAgent:
    memory = EpisodicMemory(memory_path)

    if os.environ.get("ANTHROPIC_API_KEY"):
        from .planner import ClaudePlanner
        planner = ClaudePlanner()
    else:
        planner = MockPlanner()

    return LeviAgent(planner=planner, tools=registry, memory=memory)


def main():
    parser = argparse.ArgumentParser(description="Run a task through LEVI V0.")
    parser.add_argument("task", nargs="?", help="Task description")
    parser.add_argument("--stats", action="store_true", help="Print episodic memory stats and exit")
    parser.add_argument("--recent", type=int, default=0, help="Print N most recent episodic records")
    parser.add_argument("--memory-path", default="episodic_memory.jsonl")
    args = parser.parse_args()

    agent = build_agent(args.memory_path)

    if args.stats:
        print(json.dumps(agent.memory.stats(), indent=2))
        return

    if args.recent:
        for r in agent.memory.recent(args.recent):
            print(json.dumps(r.to_dict(), indent=2))
        return

    if not args.task:
        parser.error("Provide a task, or use --stats / --recent")

    record = agent.run(args.task)
    print(f"Outcome: {record.outcome.value}")
    print(f"Notes:   {record.verifier_notes}")
    print("Plan trace:")
    for line in record.plan:
        print(f"  {line}")
    print("Actions:")
    for a in record.actions:
        print(f"  {a.tool_name}({a.tool_input}) -> {a.tool_output!r} error={a.error}")


if __name__ == "__main__":
    main()