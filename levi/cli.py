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
from .tools import registry


def build_agent(memory_path: str = "episodic_memory.jsonl") -> LeviAgent:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    memory = EpisodicMemory(memory_path)

    if os.environ.get("GEMINI_API_KEY"):
        from .planner import GeminiPlanner
        planner = GeminiPlanner()
    elif os.environ.get("ANTHROPIC_API_KEY"):
        from .planner import ClaudePlanner
        planner = ClaudePlanner()
    else:
        raise RuntimeError("No API key found. Please set GEMINI_API_KEY or ANTHROPIC_API_KEY.")

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
    
    # Format the result
    result_lines = [
        f"## Task: {args.task}",
        f"Outcome: {record.outcome.value}",
        f"Notes:   {record.verifier_notes}",
        "Plan trace:"
    ]
    for line in record.plan:
        result_lines.append(f"  {line}")
    result_lines.append("Actions:")
    for a in record.actions:
        result_lines.append(f"  {a.tool_name}({a.tool_input}) -> {a.tool_output!r} error={a.error}")
    result_lines.append("\n---\n")
    
    result_text = "\n".join(result_lines)
    
    # Print to console
    print(result_text)
    
    # Append to study file
    study_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "levi_V0_result_study.md")
    with open(study_file, "a") as f:
        f.write(result_text + "\n")


if __name__ == "__main__":
    main()