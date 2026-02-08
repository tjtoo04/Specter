"""Slack Block Kit router and multi-channel router (Slack, Teams, Discord, Jira)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from ai.config import MultiChannelConfig
from ai.models.report import IssueReport, Severity, Team

logger = logging.getLogger(__name__)

SEVERITY_EMOJI: dict[Severity, str] = {
    Severity.P0: "🔴",
    Severity.P1: "🟠",
    Severity.P2: "🟡",
    Severity.P3: "⚪",
}

CHANNEL_BY_TEAM: dict[Team, str] = {
    Team.BACKEND: "#backend-alerts",
    Team.FRONTEND: "#frontend-bugs",
    Team.UX_DESIGN: "#ux-issues",
    Team.DEVOPS: "#devops-performance",
    Team.INTEGRATION: "#integration-issues",
    Team.UNKNOWN: "#general-bugs",
}
P0_CHANNEL = "#incidents"


class AlertBackend(Protocol):
    def send(
        self,
        report: IssueReport,
        screenshot_url: str,
        test_id: str,
    ) -> str:
        ...


@dataclass
class AlertResult:
    permalink: str | None = None
    backend: str = ""
    success: bool = True
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


class AlertRouter:
    """Slack Block Kit: channel by team/severity, compose blocks, post, permalink."""

    def __init__(self, slack_token: str) -> None:
        if not slack_token or not slack_token.strip():
            raise ValueError("slack_token is required and must be non-empty")
        self._client = WebClient(token=slack_token)

    def send(
        self,
        report: IssueReport,
        screenshot_url: str,
        test_id: str,
    ) -> str:
        return self.send_alert(report, screenshot_url, test_id)

    def send_alert(
        self,
        report: IssueReport,
        screenshot_url: str,
        test_id: str,
    ) -> str:
        channel = self._get_channel(report)
        mentions = self._get_mentions(report)
        blocks = self.compose_blocks(report, screenshot_url, test_id, mentions)

        fallback_text = f"{SEVERITY_EMOJI.get(report.severity, '')} {report.title}"

        try:
            response = self._post_with_retry(channel, fallback_text, blocks)
        except SlackApiError as e:
            logger.exception("Slack chat_postMessage failed: %s", e.response.get("error"))
            raise

        if not response.get("ok"):
            raise RuntimeError(
                f"Slack API returned ok=false: {response.get('error', 'unknown')}"
            )

        channel_id = response.get("channel") or channel
        message_ts = response.get("ts")
        if not message_ts:
            return f"https://slack.com/app_redirect?channel={channel_id}"

        try:
            permalink_response = self._client.chat_getPermalink(
                channel=channel_id,
                message_ts=message_ts,
            )
            if permalink_response.get("ok") and permalink_response.get("permalink"):
                return str(permalink_response["permalink"])
        except SlackApiError as e:
            logger.warning("chat_getPermalink failed, using fallback URL: %s", e)

        return f"https://slack.com/app_redirect?channel={channel_id}&message_ts={message_ts}"

    def _post_with_retry(
        self,
        channel: str,
        text: str,
        blocks: list[dict[str, Any]],
        max_retries: int = 3,
    ) -> Any:
        import time
        last_error: Exception | None = None
        for attempt in range(max_retries):
            try:
                return self._client.chat_postMessage(
                    channel=channel,
                    text=text,
                    blocks=blocks,
                    unfurl_links=False,
                    unfurl_media=False,
                )
            except SlackApiError as e:
                last_error = e
                if e.response.status_code == 429:
                    wait = int(e.response.headers.get("Retry-After", 2 ** attempt))
                    logger.warning("Slack rate limit; retrying after %ss", wait)
                    time.sleep(wait)
                elif e.response.status_code >= 500 and attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise
        raise last_error or RuntimeError("Slack post failed after retries")

    def _get_channel(self, report: IssueReport) -> str:
        if report.severity == Severity.P0:
            return P0_CHANNEL
        return CHANNEL_BY_TEAM.get(report.team, CHANNEL_BY_TEAM[Team.UNKNOWN])

    def _get_mentions(self, report: IssueReport) -> str:
        if report.severity == Severity.P0:
            return "<!here>"
        return ""

    def compose_blocks(
        self,
        report: IssueReport,
        screenshot_url: str,
        test_id: str,
        mentions: str = "",
    ) -> list[dict[str, Any]]:
        emoji = SEVERITY_EMOJI.get(report.severity, "⚪")
        header_text = f"{emoji} {report.title}"
        if mentions:
            header_text = f"{header_text} {mentions}"

        blocks: list[dict[str, Any]] = [
            {"type": "header", "text": {"type": "plain_text", "text": header_text, "emoji": True}},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Category*\n{report.category}"},
                    {"type": "mrkdwn", "text": f"*Severity*\n{report.severity.value}"},
                    {"type": "mrkdwn", "text": f"*Team*\n{report.team.value}"},
                    {"type": "mrkdwn", "text": f"*Impact*\n{report.impact}"},
                ],
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Root cause*\n{report.root_cause}"},
            },
        ]

        # Skip placeholder image URLs so Slack doesn't fail block validation
        url = (screenshot_url or "").strip()
        if url and "example.com" not in url:
            blocks.append({
                "type": "image",
                "image_url": url,
                "alt_text": "Screenshot evidence",
                "title": {"type": "plain_text", "text": "Screenshot", "emoji": True},
            })

        steps_text = "\n".join(f"• {s}" for s in report.reproduction_steps) if report.reproduction_steps else "_None provided_"
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Reproduction steps*\n{steps_text}"},
        })

        expected_actual = (
            f"*Expected:* {report.expected_behavior}\n*Actual:* {report.actual_behavior}"
        )
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": expected_actual},
        })

        actions_text = "\n".join(f"• {a}" for a in report.recommended_actions) if report.recommended_actions else "_None provided_"
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Recommended actions*\n{actions_text}"},
        })

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"Test ID: `{test_id}`"},
                {"type": "mrkdwn", "text": f"Timestamp: {ts}"},
            ],
        })

        return blocks


class MultiChannelAlertRouter:
    """Sends one report to Slack, Teams, Discord, Jira. One AlertResult per backend."""

    def __init__(self, config: MultiChannelConfig) -> None:
        from ai.alerts.backends.teams import TeamsAlertBackend
        from ai.alerts.backends.discord import DiscordAlertBackend
        from ai.alerts.backends.webhook import WebhookAlertBackend

        self._slack_router = AlertRouter(slack_token=config.slack_token)
        self._backends = [
            ("slack", self._slack_router),
            ("teams", TeamsAlertBackend(config.teams_webhook_url)),
            ("discord", DiscordAlertBackend(config.discord_webhook_url)),
            ("webhook", WebhookAlertBackend(
                jira_url=config.jira_webhook_url,
                jira_webhook_secret=config.jira_webhook_secret,
            )),
        ]

    def get_slack_blocks(
        self,
        report: IssueReport,
        screenshot_url: str,
        test_id: str,
    ) -> list[dict[str, Any]]:
        mentions = "<!here>" if report.severity == Severity.P0 else ""
        return self._slack_router.compose_blocks(report, screenshot_url, test_id, mentions)

    def send_alert(
        self,
        report: IssueReport,
        screenshot_url: str,
        test_id: str,
    ) -> list[AlertResult]:
        results: list[AlertResult] = []
        for name, backend in self._backends:
            try:
                permalink = backend.send(report, screenshot_url, test_id)
                results.append(AlertResult(permalink=permalink, backend=name, success=True))
            except Exception as e:  # noqa: BLE001
                logger.exception("Backend %s failed", name)
                results.append(
                    AlertResult(
                        backend=name,
                        success=False,
                        error=str(e),
                    )
                )
        return results
