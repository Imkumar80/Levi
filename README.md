# LEVI V0

See [`Documentation.md`](Documentation.md) for full instructions.

## Quickstart

This project uses `uv` for dependency management.

```bash
# With a Gemini-backed planner (Requires GEMINI_API_KEY)
export GEMINI_API_KEY=your_api_key_here
uv run python -m levi.cli "find the largest file in /tmp and report its size"
```
