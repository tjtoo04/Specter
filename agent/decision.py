def decide_next_action(vision, state):
    screen = vision["screen_type"]

    # DEMO 1: Homepage
    if screen == "home":
        if "LOGIN" in vision["elements"]:
            if state["attempts_on_screen"] == 0:
                return {"action": "scroll_horizontal", "reason": "Reveal nav"}
            return {"action": "tap", "target": "LOGIN", "reason": "Try login"}

    # DEMO 2: Login screen
    if screen == "login":
        if state["attempts_on_screen"] < 2:
            return {"action": "tap", "target": "LOGIN", "reason": "Retry login"}
        return {"action": "wait", "reason": "Likely friction"}

    # DEMO 3: Error screen
    if screen == "error":
        return {"action": "stop", "reason": "Escalate UX issue"}

    return {"action": "wait"}
