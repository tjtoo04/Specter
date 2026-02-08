from agent.diagnosis import diagnose

state = {
    "current_screen_id": "signup_email",
    "time_on_screen": 18,
    "attempts_on_screen": 3,
    "history": ["welcome", "signup_email"]
}

vision = {
    "elements": ["Email field", "Continue button"],
    "error_text": None
}

result = diagnose(state, vision, "REPEATED_ACTIONS")
print(result)
