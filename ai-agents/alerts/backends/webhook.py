"""Jira webhook: POST JSON (summary, description, labels)."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from ai.models.report import IssueReport

logger = logging.getLogger(__name__)


class WebhookAlertBackend:
    """Jira webhook. Secret sent as X-Automation-Webhook-Token when set."""

    def __init__(self, jira_url: str, jira_webhook_secret: str = "") -> None:
        self._jira_url = (jira_url or "").strip()
        if not self._jira_url:
            raise ValueError("jira_webhook_url is required")
        self._jira_webhook_secret = (jira_webhook_secret or "").strip()

    def send(
        self,
        report: IssueReport,
        screenshot_url: str,
        test_id: str,
    ) -> str:
        payload = self._build_payload(report, screenshot_url, test_id)
        try:
            self._post(self._jira_url, self._jira_payload(report, payload))
            return "jira:ok"
        except Exception as e:
            logger.exception("Jira webhook failed")
            raise RuntimeError(f"Jira webhook failed: {e}") from e

    def _post(self, url: str, data: dict[str, Any]) -> None:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._jira_webhook_secret:
            headers["X-Automation-Webhook-Token"] = self._jira_webhook_secret
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status not in (200, 201, 202, 204):
                raise RuntimeError(f"Webhook returned {resp.status}")

    def _build_payload(
        self,
        report: IssueReport,
        screenshot_url: str,
        test_id: str,
    ) -> dict[str, Any]:
        steps = "\n".join(f"• {s}" for s in report.reproduction_steps)
        actions = "\n".join(f"• {a}" for a in report.recommended_actions)
        return {
            "title": report.title,
            "severity": report.severity.value,
            "team": report.team.value,
            "category": report.category,
            "impact": report.impact,
            "root_cause": report.root_cause,
            "reproduction_steps": steps,
            "expected_behavior": report.expected_behavior,
            "actual_behavior": report.actual_behavior,
            "recommended_actions": actions,
            "screenshot_url": screenshot_url or "",
            "test_id": test_id,
        }

    def _jira_payload(self, report: IssueReport, payload: dict[str, Any]) -> dict[str, Any]:
        """Shape for Jira (e.g. Automation for Jira or custom endpoint)."""
        description = (
            f"*Root cause:*\n{payload['root_cause']}\n\n"
            f"*Reproduction:*\n{payload['reproduction_steps']}\n\n"
            f"*Expected:* {payload['expected_behavior']}\n"
            f"*Actual:* {payload['actual_behavior']}\n\n"
            f"*Recommended actions:*\n{payload['recommended_actions']}\n\n"
            f"Screenshot: {payload['screenshot_url']}\nTest ID: {payload['test_id']}"
        )
        return {
            "summary": payload["title"],
            "description": description,
            "labels": [report.severity.value, report.team.value, "mystery-shopper"],
            "customfield_severity": report.severity.value,
            "customfield_team": report.team.value,
            **{k: v for k, v in payload.items() if k not in ("title", "root_cause", "reproduction_steps", "expected_behavior", "actual_behavior", "recommended_actions", "screenshot_url", "test_id")},
        }
