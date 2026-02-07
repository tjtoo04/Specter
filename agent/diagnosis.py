# agent/diagnosis.py

USE_REAL_GEMINI = False


def diagnose(state, vision, friction_type):
    """
    Entry point for Step 8 diagnosis.
    """
    if USE_REAL_GEMINI:
        return diagnose_with_gemini(state, vision, friction_type)

    return diagnose_with_fake_gemini(state, vision, friction_type)


def diagnose_with_fake_gemini(state, vision, friction_type):
    """
    Fake Gemini diagnosis for testing/demo.
    """

    if friction_type == "REPEATED_ACTIONS":
        return {
            "issue_type": "UI Bug",
            "severity": "P0",
            "root_cause": (
                "Primary action was triggered multiple times but the screen "
                "did not change, indicating a broken or unresponsive button."
            ),
            "suggested_team": "Frontend",
            "friction_type": friction_type,
            "model": "fake-gemini"
        }


    if friction_type == "TIME_STUCK":
        return {
            "issue_type": "UX Friction",
            "severity": "P1",
            "root_cause": (
                "User remained on the same screen for too long without a "
                "clear next action."
            ),
            "suggested_team": "Design",
            "friction_type": friction_type,
            "model": "fake-gemini"
        }


    if friction_type == "SCREEN_LOOP":
        return {
            "issue_type": "Navigation Failure",
            "severity": "P1",
            "root_cause": (
                "User was redirected between screens repeatedly, "
                "indicating a broken navigation flow."
            ),
            "suggested_team": "Frontend",
            "friction_type": friction_type,
            "model": "fake-gemini"
        }


    return {
        "issue_type": "Unknown",
        "severity": "P2",
        "root_cause": "Unclassified friction detected during signup.",
        "suggested_team": "QA",
        "friction_type": friction_type,
        "model": "fake-gemini"
    }


def diagnose_with_gemini(state, vision, friction_type):
    """
    Placeholder for real Gemini call.
    """
    return {
        "issue_type": "AI Disabled",
        "severity": "P3",
        "root_cause": "Real Gemini diagnosis not enabled.",
        "suggested_team": "QA",
        "friction_type": friction_type,
        "model": "disabled"
    }
