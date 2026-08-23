"""
Episodic memory schema.

Everything LEVI later consolidates into semantic/procedural memory (V1+)
is read from these records, so the fields here are deliberately structured
rather than free text. Don't loosen this later — extend it instead.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional


class Outcome(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


@dataclass
class ToolCall:
    tool_name: str
    tool_input: dict[str, Any]
    tool_output: Any
    error: Optional[str] = None
    duration_ms: Optional[float] = None


@dataclass
class EpisodicRecord:
    """One completed task attempt: plan -> actions -> outcome."""

    task: str
    plan: list[str]
    actions: list[ToolCall]
    outcome: Outcome
    verifier_notes: str = ""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    source: str = "agent_run"          # who/what produced this record
    scope: str = "private"             # "private" | "shared" (V2)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["outcome"] = self.outcome.value
        return d

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "EpisodicRecord":
        d = dict(d)
        d["outcome"] = Outcome(d["outcome"])
        d["actions"] = [ToolCall(**a) for a in d["actions"]]
        return EpisodicRecord(**d)