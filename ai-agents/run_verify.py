"""Verify alert pipeline: dry run or --send to all backends. Requires ai/.env."""

from __future__ import annotations

import argparse
import json
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true", help="Send to Slack, Teams, Discord, Jira")
    parser.add_argument("--show-blocks", action="store_true", help="Print Slack blocks JSON")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    try:
        from ai.config import load_config
    except ImportError as e:
        print("[FAIL] Cannot import ai.config:", e)
        return 1

    try:
        config = load_config()
    except ValueError as e:
        print("[FAIL]", e)
        print("Copy ai/.env.example to ai/.env and set all required variables.")
        return 1

    from ai.models.report import IssueReport, Severity, Team
    from ai.alerts import MultiChannelAlertRouter
    from ai.routing import RoutingAgent

    report = IssueReport(
        title="[Verify] Signup form fails on iOS Safari with autofill",
        severity=Severity.P1,
        team=Team.UNKNOWN,
        category="Regression",
        impact="Users cannot complete signup on iOS.",
        root_cause="Autofill triggers blur before validation runs.",
        reproduction_steps=[
            "Open signup on iOS Safari",
            "Use system autofill and submit",
        ],
        expected_behavior="Email retained and form validates.",
        actual_behavior="Email empty at submit.",
        recommended_actions=["Debounce validation", "Add E2E for autofill"],
    )
    screenshot_url = "https://example.com/screenshot.png"
    test_id = "verify-run-001"

    agent = RoutingAgent(config.gemini_api_key, config.gemini_model)
    routed = agent.enrich(report, screenshot_url, test_id)
    report, screenshot_url, test_id = routed.report, routed.screenshot_url, routed.test_id

    router = MultiChannelAlertRouter(config)
    print("[OK] Config loaded, Routing Agent + MultiChannelAlertRouter ready")
    print("[OK] IssueReport built:", report.title[:50], "... (team:", report.team.value + ")")

    blocks = router.get_slack_blocks(report, screenshot_url, test_id)
    print("[OK] Slack Block Kit blocks composed:", len(blocks), "blocks")

    if args.show_blocks:
        print("\n--- Slack blocks JSON ---")
        print(json.dumps(blocks, indent=2))

    if args.send:
        results = router.send_alert(report, screenshot_url, test_id)
        print("\n[OK] Sent to all backends:")
        for r in results:
            status = "OK" if r.success else "FAIL"
            print(f"  {r.backend}: [{status}]", r.permalink or r.error or "")
        return 0

    print("\n[OK] Dry run complete. Use --send to send to all backends.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
