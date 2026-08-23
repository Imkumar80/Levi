"""
Planner.

V0 note: deliberately ReAct-style (observe -> decide next tool call -> repeat)
rather than ReWOO (plan everything up front, then execute blind). ReWOO's
plan-once-execute-without-replanning shape pays off on cost/latency, but
adds a real debugging constraint. Swap PlannerBase implementations once
the memory subsystem is stable and you want to experiment with that
tradeoff — nothing else in the loop needs to change.

Two implementations:
  - MockPlanner: no API calls, deterministic, lets you test the full
    agent/memory/verifier loop offline.
  - ClaudePlanner: real planning via the Anthropic API. Requires
    ANTHROPIC_API_KEY in the environment.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, Optional

from .tools import ToolRegistry


class PlannerBase(ABC):
    @abstractmethod
    def next_step(
        self,
        task: str,
        tool_names: list[str],
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Return either:
          {"done": True, "reasoning": "..."}
        or:
          {"done": False, "tool": "<name>", "tool_input": {...}, "reasoning": "..."}
        """
        raise NotImplementedError


class MockPlanner(PlannerBase):
    """
    Deterministic stand-in planner for offline testing.
    Very naive: if the task mentions a calculator-friendly expression, use
    it once and stop. Otherwise echoes the task. Replace with ClaudePlanner
    for real use.
    """

    def next_step(self, task, tool_names, history):
        if history:
            return {"done": True, "reasoning": "Single-step mock planner: done after one action."}

        import re
        expr_match = re.search(r"[\d\.\s\+\-\*/\(\)]{3,}", task)
        if expr_match and "calculator" in tool_names:
            return {
                "done": False,
                "tool": "calculator",
                "tool_input": {"expression": expr_match.group().strip()},
                "reasoning": "Task looks like an arithmetic expression.",
            }
        return {
            "done": False,
            "tool": "echo",
            "tool_input": {"text": task},
            "reasoning": "No specialized tool matched; echoing task.",
        }


class ClaudePlanner(PlannerBase):
    """Real planner backed by the Anthropic API. Requires the `anthropic` package."""

    def __init__(self, model: str = "claude-sonnet-4-6", api_key: Optional[str] = None):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def next_step(self, task, tool_names, history):
        system = (
            "You are LEVI's planner. Given a task, available tools, and the "
            "history of actions taken so far, decide the single next action.\n"
            f"Available tools: {tool_names}\n"
            "Respond with ONLY a JSON object, no other text, matching one of:\n"
            '{"done": false, "tool": "<name>", "tool_input": {...}, "reasoning": "..."}\n'
            '{"done": true, "reasoning": "..."}'
        )
        user = json.dumps({"task": task, "history": history})

        resp = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)