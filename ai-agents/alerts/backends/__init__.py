"""Alert backends: Slack (in alerts.py), Teams, Discord, Jira webhooks."""

from ai.alerts.backends.teams import TeamsAlertBackend
from ai.alerts.backends.discord import DiscordAlertBackend
from ai.alerts.backends.webhook import WebhookAlertBackend

__all__ = [
    "TeamsAlertBackend",
    "DiscordAlertBackend",
    "WebhookAlertBackend",
]
