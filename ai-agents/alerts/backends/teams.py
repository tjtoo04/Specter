"""Teams webhook: Adaptive Card payloads."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from ai.models.report import IssueReport, Severity

logger = logging.getLogger(__name__)

SEVERITY_EMOJI = {
    Severity.P0: "🔴",
    Severity.P1: "🟠",
    Severity.P2: "🟡",
    Severity.P3: "⚪",
}


class TeamsAlertBackend:
    def __init__(self, webhook_url: str) -> None:
        if not webhook_url or not webhook_url.strip():
            raise ValueError("teams_webhook_url is required")
        self._webhook_url = webhook_url.strip()

    def send(
        self,
        report: IssueReport,
        screenshot_url: str,
        test_id: str,
    ) -> str:
        card = self._build_adaptive_card(report, screenshot_url, test_id)
        payload = {"type": "message", "attachments": [{"contentType": "application/vnd.microsoft.card.adaptive", "content": card}]}

        req = urllib.request.Request(
            self._webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status not in (200, 201, 202):
                    raise RuntimeError(f"Teams webhook returned {resp.status}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            logger.error("Teams webhook HTTP error: %s %s", e.code, body)
            raise RuntimeError(f"Teams webhook failed: {e.code} - {body}") from e
        except urllib.error.URLError as e:
            logger.exception("Teams webhook request failed")
            raise RuntimeError(f"Teams webhook request failed: {e}") from e

        return self._webhook_url

    def _build_adaptive_card(
        self,
        report: IssueReport,
        screenshot_url: str,
        test_id: str,
    ) -> dict[str, Any]:
        """Build Adaptive Card JSON (v1.2)."""
        emoji = SEVERITY_EMOJI.get(report.severity, "⚪")
        title = f"{emoji} {report.title}"

        facts: list[dict[str, str]] = [
            {"title": "Category", "value": report.category},
            {"title": "Severity", "value": report.severity.value},
            {"title": "Team", "value": report.team.value},
            {"title": "Impact", "value": report.impact},
            {"title": "Test ID", "value": test_id},
        ]

        body: list[dict[str, Any]] = [
            {"type": "TextBlock", "text": title, "size": "large", "weight": "bolder", "wrap": True},
            {"type": "FactSet", "facts": facts},
            {"type": "TextBlock", "text": "**Root cause**", "weight": "bolder", "wrap": True},
            {"type": "TextBlock", "text": report.root_cause, "wrap": True},
            {"type": "TextBlock", "text": "**Reproduction steps**", "weight": "bolder", "wrap": True},
            {"type": "TextBlock", "text": "\n".join(f"• {s}" for s in report.reproduction_steps) or "—", "wrap": True},
            {"type": "TextBlock", "text": f"**Expected:** {report.expected_behavior}", "wrap": True},
            {"type": "TextBlock", "text": f"**Actual:** {report.actual_behavior}", "wrap": True},
            {"type": "TextBlock", "text": "**Recommended actions**", "weight": "bolder", "wrap": True},
            {"type": "TextBlock", "text": "\n".join(f"• {a}" for a in report.recommended_actions) or "—", "wrap": True},
        ]

        if screenshot_url and screenshot_url.strip():
            body.append({
                "type": "Image",
                "url": screenshot_url.strip(),
                "altText": "Screenshot evidence",
            })

        return {"type": "AdaptiveCard", "$schema": "http://adaptivecards.io/schemas/adaptive-card.json", "version": "1.2", "body": body}
