"""Example: load config, enrich report via RoutingAgent, send to all backends."""

from __future__ import annotations

import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from ai.config import load_config
from ai.models.report import IssueReport, Severity, Team
from ai.alerts import MultiChannelAlertRouter
from ai.routing import RoutingAgent


def build_sample_report() -> IssueReport:
    return IssueReport(
        title="Signup form fails on iOS Safari with autofill",
        severity=Severity.P1,
        team=Team.UNKNOWN,
        category="Regression",
        impact="Users cannot complete signup on iOS; conversion drop.",
        root_cause="Autofill triggers blur before our validation runs; state is stale.",
        reproduction_steps=[
            "Open signup on iOS Safari",
            "Tap email field and use system autofill",
            "Tap password and submit",
            "Form submits with empty email",
        ],
        expected_behavior="Email field retains autofill value and form validates.",
        actual_behavior="Email is empty at submit; validation passes due to race.",
        recommended_actions=[
            "Debounce validation and re-run on blur",
            "Use native form validation as fallback",
            "Add E2E test for iOS Safari autofill flow",
        ],
        metadata={"related_issues": ["PROJ-123"]},
    )


def main() -> None:
    try:
        config = load_config()
    except ValueError as e:
        print("Config error:", e)
        print("Copy ai/.env.example to ai/.env and set all required variables.")
        sys.exit(1)

    report = build_sample_report()
    screenshot_url = "https://example.com/screenshots/signup-bug.png"
    test_id = "ms-run-20260207-001"

    agent = RoutingAgent(config.gemini_api_key, config.gemini_model)
    routed = agent.enrich(report, screenshot_url, test_id)

    router = MultiChannelAlertRouter(config)
    results = router.send_alert(routed.report, routed.screenshot_url, routed.test_id)

    print("Results (team assigned by agent:", routed.report.team.value + "):")
    for r in results:
        status = "OK" if r.success else "FAIL"
        print(f"  {r.backend}: [{status}]", r.permalink or r.error or "")


if __name__ == "__main__":
    main()
