"""Alert config: env loading and validation. All keys in _REQUIRED_ENV_KEYS must be set."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_REQUIRED_ENV_KEYS = [
    "SLACK_BOT_TOKEN",
    "TEAMS_WEBHOOK_URL",
    "DISCORD_WEBHOOK_URL",
    "JIRA_WEBHOOK_URL",
    "GEMINI_API_KEY",
]


def load_dotenv_if_available(env_path: Path | None = None) -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    path = env_path if env_path and env_path.is_file() else Path(__file__).resolve().parent / ".env"
    if path.is_file():
        load_dotenv(path)


def _get_env(key: str, default: str = "") -> str:
    return (os.environ.get(key) or default).strip()


def _missing_keys() -> list[str]:
    return [k for k in _REQUIRED_ENV_KEYS if not _get_env(k)]


@dataclass(frozen=True)
class MultiChannelConfig:
    """Backend URLs/tokens and Gemini settings. Use load_config() to build."""

    slack_token: str
    teams_webhook_url: str
    discord_webhook_url: str
    jira_webhook_url: str
    jira_webhook_secret: str
    gemini_api_key: str
    gemini_model: str

    def __post_init__(self) -> None:
        required = [
            ("slack_token", self.slack_token),
            ("teams_webhook_url", self.teams_webhook_url),
            ("discord_webhook_url", self.discord_webhook_url),
            ("jira_webhook_url", self.jira_webhook_url),
            ("gemini_api_key", self.gemini_api_key),
        ]
        missing = [name for name, val in required if not (val and str(val).strip())]
        if missing:
            raise ValueError(f"MultiChannelConfig missing required: {', '.join(missing)}")


def load_config(env_path: Path | None = None) -> MultiChannelConfig:
    """Load from env_path or ai/.env. Raises ValueError if any required key is missing."""
    load_dotenv_if_available(env_path)

    missing = _missing_keys()
    if missing:
        raise ValueError(
            "Alert config incomplete. Set these in ai/.env (all required): "
            + ", ".join(missing)
        )

    return MultiChannelConfig(
        slack_token=_get_env("SLACK_BOT_TOKEN"),
        teams_webhook_url=_get_env("TEAMS_WEBHOOK_URL"),
        discord_webhook_url=_get_env("DISCORD_WEBHOOK_URL"),
        jira_webhook_url=_get_env("JIRA_WEBHOOK_URL"),
        jira_webhook_secret=_get_env("JIRA_WEBHOOK_SECRET"),
        gemini_api_key=_get_env("GEMINI_API_KEY"),
        gemini_model=_get_env("GEMINI_MODEL") or "gemini-2.5-flash",
    )


def validate_env(env_path: Path | None = None) -> list[str]:
    """Return missing required env keys. Empty list => valid."""
    load_dotenv_if_available(env_path)
    return _missing_keys()
