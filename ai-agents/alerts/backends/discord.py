"""Discord webhook: rich embed with severity color."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from ai.models.report import IssueReport, Severity

logger = logging.getLogger(__name__)

SEVERITY_COLOR = {
    Severity.P0: 0xE74C3C,   # red
    Severity.P1: 0xE67E22,   # orange
    Severity.P2: 0xF1C40F,   # yellow
    Severity.P3: 0x95A5A6,   # gray
}


class DiscordAlertBackend:
    def __init__(self, webhook_url: str) -> None:
        if not webhook_url or not webhook_url.strip():
            raise ValueError("discord_webhook_url is required")
        self._webhook_url = webhook_url.strip()

    def send(
        self,
        report: IssueReport,
        screenshot_url: str,
        test_id: str,
    ) -> str:
        payload = self._build_payload(report, screenshot_url, test_id)

        req = urllib.request.Request(
            self._webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "MysteryShopper-Alerts/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status not in (200, 204):
                    raise RuntimeError(f"Discord webhook returned {resp.status}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            logger.error("Discord webhook HTTP error: %s %s", e.code, body)
            raise RuntimeError(f"Discord webhook failed: {e.code} - {body}") from e
        except urllib.error.URLError as e:
            logger.exception("Discord webhook request failed")
            raise RuntimeError(f"Discord webhook request failed: {e}") from e

        return self._webhook_url

    def _build_payload(
        self,
        report: IssueReport,
        screenshot_url: str,
        test_id: str,
    ) -> dict[str, Any]:
        """Build webhook payload with embed and optional image."""
        color = SEVERITY_COLOR.get(report.severity, 0x95A5A6)

        steps = "\n".join(f"• {s}" for s in report.reproduction_steps) if report.reproduction_steps else "—"
        actions = "\n".join(f"• {a}" for a in report.recommended_actions) if report.recommended_actions else "—"

        embed: dict[str, Any] = {
            "title": report.title,
            "color": color,
            "fields": [
                {"name": "Category", "value": report.category, "inline": True},
                {"name": "Severity", "value": report.severity.value, "inline": True},
                {"name": "Team", "value": report.team.value, "inline": True},
                {"name": "Impact", "value": report.impact, "inline": False},
                {"name": "Root cause", "value": report.root_cause[:1024] or "—", "inline": False},
                {"name": "Reproduction steps", "value": steps[:1024] or "—", "inline": False},
                {"name": "Expected", "value": report.expected_behavior[:1024] or "—", "inline": False},
                {"name": "Actual", "value": report.actual_behavior[:1024] or "—", "inline": False},
                {"name": "Recommended actions", "value": actions[:1024] or "—", "inline": False},
                {"name": "Test ID", "value": test_id, "inline": True},
            ],
        }
        if screenshot_url and screenshot_url.strip():
            embed["image"] = {"url": screenshot_url.strip()}

        return {"embeds": [embed]}
