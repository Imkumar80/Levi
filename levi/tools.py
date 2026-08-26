"""
Tool executor.

A tool is just a name + a callable(**kwargs) -> Any. Keep tools small,
pure where possible, and let them raise exceptions on failure — the
executor catches those and records them as errors rather than crashing
the agent loop.
"""

from __future__ import annotations

import time
from typing import Any, Callable

from .schema import ToolCall


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, name: str):
        def decorator(fn: Callable[..., Any]):
            self._tools[name] = fn
            return fn
        return decorator

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def run(self, name: str, **kwargs) -> ToolCall:
        if name not in self._tools:
            return ToolCall(
                tool_name=name, tool_input=kwargs, tool_output=None,
                error=f"Unknown tool: {name}. Available: {self.names()}",
            )
        start = time.time()
        try:
            output = self._tools[name](**kwargs)
            return ToolCall(
                tool_name=name, tool_input=kwargs, tool_output=output,
                error=None, duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            return ToolCall(
                tool_name=name, tool_input=kwargs, tool_output=None,
                error=str(e), duration_ms=(time.time() - start) * 1000,
            )


# --- example V0 tools. Replace/extend with real ones (shell, file IO, http, etc). ---

registry = ToolRegistry()


@registry.register("calculator")
def calculator(expression: str) -> float:
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        raise ValueError(f"Unsafe expression: {expression}")
    return eval(expression, {"__builtins__": {}}, {})


@registry.register("echo")
def echo(text: str) -> str:
    return text


@registry.register("write_file")
def write_file(path: str, content: str) -> str:
    from pathlib import Path
    Path(path).write_text(content)
    return f"wrote {len(content)} chars to {path}"


@registry.register("read_file")
def read_file(path: str) -> str:
    from pathlib import Path
    return Path(path).read_text()


@registry.register("run_command")
def run_command(command: str) -> str:
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}\nStderr: {result.stderr}")
    return result.stdout