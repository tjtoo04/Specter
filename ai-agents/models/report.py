"""IssueReport, Severity, Team. Core payload for routing and alerts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class Team(str, Enum):
    BACKEND = "Backend"
    FRONTEND = "Frontend"
    UX_DESIGN = "UX/Design"
    DEVOPS = "DevOps"
    INTEGRATION = "Integration"
    UNKNOWN = "Unknown"


@dataclass(frozen=False)
class IssueReport:
    title: str
    severity: Severity
    team: Team
    category: str
    impact: str
    root_cause: str
    reproduction_steps: list[str]
    expected_behavior: str
    actual_behavior: str
    recommended_actions: list[str]
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.title or not self.root_cause:
            raise ValueError("title and root_cause are required")
        if not isinstance(self.reproduction_steps, list):
            self.reproduction_steps = list(self.reproduction_steps) if self.reproduction_steps else []
        if not isinstance(self.recommended_actions, list):
            self.recommended_actions = (
                list(self.recommended_actions) if self.recommended_actions else []
            )
