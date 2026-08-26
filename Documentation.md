# LEVI V0 — Working Agent Loop

Minimal, real implementation of the loop:

```
Task -> Plan -> Execute tools -> Verify -> Episodic Memory
```

No memory router, no Wiki, no scoping yet — those are V1+. The goal of
V0 is to get this loop solid and produce well-structured episodic
records, because everything V1 consolidation does later reads from
`schema.py`'s `EpisodicRecord`.

## Files

| File | Role |
|---|---|
| `schema.py` | `EpisodicRecord` / `ToolCall` — the structured record format. Extend, don't loosen. |
| `memory.py` | `EpisodicMemory` — JSONL-backed store with structured (non-vector) retrieval: by tag, by outcome, task substring, recency. |
| `tools.py` | `ToolRegistry` — action space. Ships with `calculator`, `echo`, `read_file`, `write_file` as examples. |
| `verifier.py` | Deliberately dumb rule-based pass/fail. Its job is architectural (nothing skips verification), not smart. |
| `planner.py` | `GeminiPlanner` and `ClaudePlanner` (real API calls). ReAct-style, not ReWOO — see docstring for why. |
| `agent.py` | `LeviAgent` — wires planner + tools + memory + verifier into the loop. |
| `cli.py` | Manual test runner. |

## Run it

Using `uv` for dependency management, you can run the agent as follows:

```bash

# Inspect what's been recorded
uv run python -m levi.cli --stats
uv run python -m levi.cli --recent 3

# With a real Gemini-backed planner (Recommended)
export GEMINI_API_KEY=AIza...
uv run python -m levi.cli "find the largest file in /tmp and report its size"

# With a real Claude-backed planner
export ANTHROPIC_API_KEY=sk-...
uv run python -m levi.cli "find the largest file in /tmp and report its size"
```

## How we plan to Extend it

- **New tool**: add a function to `tools.py` decorated with `@registry.register("name")`.
- **New verifier logic**: edit `verify()` in `verifier.py` — keep it separate from planning logic.
- **Swap planner**: implement `PlannerBase.next_step` — the agent loop doesn't change.

## Where V1 picks up

V1 is about consolidation: reading batches of `EpisodicRecord`s
via `memory.all()` / `memory.by_tag()` / etc., extracting repeated
patterns, and writing them out as linked Wiki pages (semantic memory).
The episodic store here is the input to that step — don't build V1
consolidation until this loop has produced enough real (not synthetic)
episodic records to consolidate from.