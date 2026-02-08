from ai.models.report import IssueReport, Severity, Team


def to_issue_report(
    diagnosis: dict,
    vision: dict,
    test_id: str,
) -> IssueReport:
    """
    Translate agent diagnosis + vision into Cindy's IssueReport.
    """

    severity_map = {
        "P0": Severity.P0,
        "P1": Severity.P1,
        "P2": Severity.P2,
        "P3": Severity.P3,
    }

    team_map = {
        "Frontend": Team.FRONTEND,
        "Backend": Team.BACKEND,
        "UX": Team.UX_DESIGN,
        "DevOps": Team.DEVOPS,
    }

    severity = severity_map.get(diagnosis.get("severity"), Severity.P2)
    team = team_map.get(diagnosis.get("suggested_team"), Team.UNKNOWN)

    screen_type = vision.get("screen_type", "unknown")

    return IssueReport(
        title=f"{diagnosis.get('issue_type')} detected on {screen_type} screen",
        severity=severity,
        team=team,
        category=diagnosis.get("issue_type", "Unknown"),
        impact="User unable to progress through flow",
        root_cause=diagnosis.get("root_cause", "Unknown root cause"),
        reproduction_steps=[
            f"Navigate to {screen_type} screen",
            "Perform primary user action",
            "Observe no screen transition",
        ],
        expected_behavior="User action triggers screen transition or feedback",
        actual_behavior="User action has no visible effect",
        recommended_actions=[
            "Verify click handler binding",
            "Add loading or disabled state",
            "Add automated regression test",
        ],
        metadata={
            "friction_type": diagnosis.get("friction_type"),
            "test_id": test_id,
        },
    )

