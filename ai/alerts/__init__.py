"""Alert routing for bug reports: Slack, Teams, Discord, webhooks. All backends mandatory."""

from ai.config import MultiChannelConfig
from ai.alerts.alerts import (
    AlertResult,
    AlertRouter,
    MultiChannelAlertRouter,
)

__all__ = [
    "AlertResult",
    "AlertRouter",
    "MultiChannelAlertRouter",
    "MultiChannelConfig",
]
