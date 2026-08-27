# LEVI V0

See [`Documentation.md`](Documentation.md) for full instructions.

## Quickstart

This project uses `uv` for dependency management.

```bash
# With a Gemini-backed planner (Requires GEMINI_API_KEY)
export GEMINI_API_KEY=your_api_key_here
uv run python -m levi.cli "find the largest file in /tmp and report its size"
```

## Controlled memory-scaling evaluation

The scaling harness evaluates the existing vectorless retriever under
controlled memory-pool size, distractor-density, duplicate-rate, and
memory-management-policy conditions. It is offline and reproducible; it does
not make model calls.

```bash
uv run python evals/generate_mock_memory.py
uv run python evals/run_memory_scaling.py
```

It writes `evals/memory_scaling_results.csv`. `replay_context_success` means
the required memory entered the retrieved context window. It is a retrieval
proxy, not an end-to-end LLM task-success metric.
