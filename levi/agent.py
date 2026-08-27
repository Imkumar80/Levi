"""
LEVI V0 agent loop.

    Task -> Plan (step by step) -> Execute tools -> Verify -> Episodic Memory

This is intentionally the whole V0 scope. No memory router (only one
memory type exists yet), no consolidation, no scoping. Those are V1+
(see project notes, Section 21). Get this loop solid first.
"""

from __future__ import annotations

from dataclasses import dataclass
from .memory import EpisodicMemory
from .planner import PlannerBase
from .schema import EpisodicRecord, ToolCall
from .tools import ToolRegistry
from . import verifier


@dataclass
class AgentRunResult:
    record: EpisodicRecord
    prompt_tokens: int
    output_tokens: int
    total_tokens: int


class LeviAgent:
    def __init__(
        self,
        planner: PlannerBase,
        tools: ToolRegistry,
        memory: EpisodicMemory,
        max_steps: int = 8,
    ):
        self.planner = planner
        self.tools = tools
        self.memory = memory
        self.max_steps = max_steps

    def run(self, task: str, tags: list[str] | None = None, use_memory: bool = True, read_only_memory: bool = False) -> AgentRunResult:
        plan_log: list[str] = []
        actions: list[ToolCall] = []
        history: list[dict] = []
        
        memories = None
        if use_memory:
            memories = self.memory.retrieve(task)
            
        if hasattr(self.planner, "reset_session_stats"):
            self.planner.reset_session_stats()

        for step in range(self.max_steps):
            decision = self.planner.next_step(task, self.tools.names(), history, memories)

            if decision.get("done"):
                plan_log.append(f"[stop] {decision.get('reasoning', '')}")
                break

            tool_name = decision.get("tool")
            tool_input = decision.get("tool_input", {})
            reasoning = decision.get("reasoning", "")
            
            # Defensive check if model hallucinated tool output instead of done
            if not tool_name:
                plan_log.append(f"[stop] {reasoning}")
                break
                
            plan_log.append(f"[step {step}] {reasoning} -> {tool_name}({tool_input})")

            call = self.tools.run(tool_name, **tool_input)
            actions.append(call)

            history.append({
                "tool": tool_name,
                "tool_input": tool_input,
                "tool_output": call.tool_output,
                "error": call.error,
            })

            if call.error:
                # Let the loop continue — the planner may retry or the
                # verifier may downgrade this to PARTIAL/FAILURE.
                pass

        outcome, notes = verifier.verify(task, actions)

        record = EpisodicRecord(
            task=task,
            plan=plan_log,
            actions=actions,
            outcome=outcome,
            verifier_notes=notes,
            tags=tags or [],
        )
        
        if not read_only_memory:
            self.memory.write(record)
            
        prompt_tokens = getattr(self.planner, "session_prompt_tokens", 0)
        output_tokens = getattr(self.planner, "session_output_tokens", 0)
        
        return AgentRunResult(
            record=record,
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
            total_tokens=prompt_tokens + output_tokens
        )