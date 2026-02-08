"""Team assignment rules (keyword → team), alert summary formatting, context link extraction."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ai.models.report import IssueReport, Team


@dataclass
class TeamAssignmentRule:
    """Keyword/pattern → team. First match wins."""

    patterns: list[str]
    team: Team


TEAM_ASSIGNMENT_RULES: list[TeamAssignmentRule] = [
    TeamAssignmentRule(
        patterns=["api", "backend", "database", "server", "endpoint", "graphql", "rest"],
        team=Team.BACKEND,
    ),
    TeamAssignmentRule(
        patterns=["signup", "login", "auth", "ui", "frontend", "react", "vue", "safari", "browser", "form", "button"],
        team=Team.FRONTEND,
    ),
    TeamAssignmentRule(
        patterns=["ux", "design", "accessibility", "a11y", "layout", "mobile"],
        team=Team.UX_DESIGN,
    ),
    TeamAssignmentRule(
        patterns=["deploy", "ci/cd", "docker", "kubernetes", "performance", "latency", "infra"],
        team=Team.DEVOPS,
    ),
    TeamAssignmentRule(
        patterns=["integration", "webhook", "third-party", "oauth", "sso"],
        team=Team.INTEGRATION,
    ),
]


def assign_team_by_rules(report: IssueReport) -> Team:
    if report.team != Team.UNKNOWN:
        return report.team
    text = f"{report.title} {report.root_cause} {report.category} {report.impact}".lower()
    for rule in TEAM_ASSIGNMENT_RULES:
        for pat in rule.patterns:
            if pat.lower() in text or re.search(pat, text, re.I):
                return rule.team
    return Team.UNKNOWN


def format_alert_summary(report: IssueReport, max_length: int = 120) -> str:
    s = f"[{report.severity.value}] {report.title}"
    if len(s) > max_length:
        s = s[: max_length - 3] + "..."
    return s


def extract_context_links(report: IssueReport) -> list[str]:
    links: list[str] = []
    meta = getattr(report, "metadata", None) or {}
    if isinstance(meta, dict):
        for key in ("related_issues", "context_links", "component_urls"):
            val = meta.get(key)
            if isinstance(val, list):
                links.extend(str(x) for x in val)
            elif isinstance(val, str):
                links.append(val)
    return links
