def detect_friction(state):
    """
    Detect if the agent is experiencing friction (stuck/confused).
    Returns (is_stuck: bool, friction_type: str | None)
    """

    # RULE 1: Too long on same screen
    if state.get("time_on_screen", 0) > 15:
        return True, "TIME_STUCK"

    # RULE 2: Too many attempts on same screen
    if state.get("attempts_on_screen", 0) >= 3:
        return True, "REPEATED_ACTIONS"

    # RULE 3: Screen loop
    if state.get("screen_repeat_count", 0) >= 2:
        return True, "SCREEN_LOOP"

    # RULE 4: Action failed
    if not state.get("action_succeeded", True):
        return True, "ACTION_FAILED"

    return False, None
