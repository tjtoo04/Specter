"""RoutedAlert: enriched report + screenshot_url, test_id, optional context/summary."""

from __future__ import annotations

from dataclasses import dataclass

from ai.models.report import IssueReport


@dataclass
class RoutedAlert:
    report: IssueReport
    screenshot_url: str
    test_id: str
    context_links: list[str] | None = None
    formatted_summary: str | None = None
