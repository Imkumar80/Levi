"""
LEVI V0 agent loop.

    Task -> Plan (step by step) -> Execute tools -> Verify -> Episodic Memory

This is intentionally the whole V0 scope. No memory router (only one
memory type exists yet), no consolidation, no scoping. Those are V1+
(see project notes, Section 21). Get this loop solid first.
"""

from __future__ import annotations

from .memory import EpisodicMemory
from .planner import PlannerBase
from .schema import EpisodicRecord, ToolCall
from .tools import ToolRegistry
from . import verifier


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

    def run(self, task: str, tags: list[str] | None = None) -> EpisodicRecord:
        plan_log: list[str] = []
        actions: list[ToolCall] = []
        history: list[dict] = []

        for step in range(self.max_steps):
            decision = self.planner.next_step(task, self.tools.names(), history)

            if decision.get("done"):
                plan_log.append(f"[stop] {decision.get('reasoning', '')}")
                break

            tool_name = decision["tool"]
            tool_input = decision.get("tool_input", {})
            reasoning = decision.get("reasoning", "")
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
        self.memory.write(record)
        return record