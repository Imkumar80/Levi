"""
Planner.

V0 note: deliberately ReAct-style (observe -> decide next tool call -> repeat)
rather than ReWOO (plan everything up front, then execute blind). ReWOO's
plan-once-execute-without-replanning shape pays off on cost/latency, but
adds a real debugging constraint. Swap PlannerBase implementations once
the memory subsystem is stable and you want to experiment with that
tradeoff — nothing else in the loop needs to change.

Two implementations:
  - ClaudePlanner: real planning via the Anthropic API. Requires
    ANTHROPIC_API_KEY in the environment.
  - GeminiPlanner: real planning via the Gemini API. Requires
    GEMINI_API_KEY in the environment and `google-genai` package.
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
        memories: list[Any] | None = None,
    ) -> dict[str, Any]:
        """
        Return either:
          {"done": True, "reasoning": "..."}
        or:
          {"done": False, "tool": "<name>", "tool_input": {...}, "reasoning": "..."}
        """
        raise NotImplementedError


class ClaudePlanner(PlannerBase):
    """Real planner backed by the Anthropic API. Requires the `anthropic` package."""

    def __init__(self, model: str = "claude-sonnet-4-6", api_key: Optional[str] = None):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def next_step(self, task, tool_names, history, memories=None):
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


class GeminiPlanner(PlannerBase):
    """Real planner backed by the Gemini API. Requires the `google-genai` package."""

    def __init__(self, model: str = "gemini-3.6-flash", api_key: Optional[str] = None):
        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.session_prompt_tokens = 0
        self.session_output_tokens = 0
        
    def reset_session_stats(self):
        self.session_prompt_tokens = 0
        self.session_output_tokens = 0

    def next_step(self, task, tool_names, history, memories=None):
        system_instruction = (
            "You are LEVI's planner. Given a task, available tools, and the "
            "history of actions taken so far, decide the single next action.\n"
            f"Available tools: {tool_names}\n"
        )
        
        if memories:
            system_instruction += "\nRelevant Past Experiences:\n"
            for m in memories:
                # Provide task, plan logic, actions, and outcome as a string
                exp = f"Task: {m.task}\nOutcome: {m.outcome.value}\nActions Taken: {json.dumps([{'tool': a.tool_name, 'input': a.tool_input, 'output': a.tool_output} for a in m.actions])}\n"
                system_instruction += exp + "\n"
                
        system_instruction += (
            "Respond with ONLY a JSON object, no other text, matching one of:\n"
            '{"done": false, "tool": "<name>", "tool_input": {...}, "reasoning": "..."}\n'
            '{"done": true, "reasoning": "..."}'
        )
        
        user = json.dumps({"task": task, "history": history})

        from google.genai import types
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.0,
        )

        resp = self.client.models.generate_content(
            model=self.model,
            contents=user,
            config=config,
        )
        
        if getattr(resp, "usage_metadata", None):
            self.session_prompt_tokens += getattr(resp.usage_metadata, "prompt_token_count", 0)
            self.session_output_tokens += getattr(resp.usage_metadata, "candidates_token_count", 0)
        
        text = resp.text.strip()
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)