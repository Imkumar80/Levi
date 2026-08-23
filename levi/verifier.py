"""
Verifier.

V0 rule: keep this dumb on purpose. The point of having a Verifier slot
in the loop at all is architectural — nothing reaches episodic memory
without passing through a pass/fail judgment, so the agent can't quietly
learn from things that merely *looked* like they worked.

Upgrade path (not V0): LLM-graded verification against task intent,
external checks (tests passing, schema validation), human-in-the-loop
confirmation.
"""

from __future__ import annotations

from .schema import Outcome, ToolCall


def verify(task: str, actions: list[ToolCall]) -> tuple[Outcome, str]:
    if not actions:
        return Outcome.FAILURE, "No actions were taken."

    errors = [a for a in actions if a.error]
    if errors:
        if len(errors) == len(actions):
            return Outcome.FAILURE, f"All {len(errors)} action(s) errored."
        return Outcome.PARTIAL, f"{len(errors)}/{len(actions)} action(s) errored."

    last = actions[-1]
    if last.tool_output in (None, ""):
        return Outcome.PARTIAL, "Last action produced no output."

    return Outcome.SUCCESS, "All actions completed without error."