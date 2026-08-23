
## Files

| File | Role |
|---|---|
| `schema.py` | `EpisodicRecord` / `ToolCall` — the structured record format. Extend, don't loosen. |
| `memory.py` | `EpisodicMemory` — JSONL-backed store with structured (non-vector) retrieval: by tag, by outcome, task substring, recency. |
| `tools.py` | `ToolRegistry` — action space. Ships with `calculator`, `echo`, `read_file`, `write_file` as examples. |
| `verifier.py` | Deliberately dumb rule-based pass/fail. Its job is architectural (nothing skips verification), not smart. |
| `planner.py` | `MockPlanner` (offline, deterministic) and `ClaudePlanner` (real API calls). ReAct-style, not ReWOO — see docstring for why. |
| `agent.py` | `LeviAgent` — wires planner + tools + memory + verifier into the loop. |
| `cli.py` | Manual test runner. |

## Run it

```bash
# No API key needed — uses MockPlanner
python -m levi.cli "12 * (3 + 4)"

# Inspect what's been recorded
python -m levi.cli --stats
python -m levi.cli --recent 3

# With a real Claude-backed planner
export ANTHROPIC_API_KEY=sk-...
python -m levi.cli "find the largest file in /tmp and report its size"
```
