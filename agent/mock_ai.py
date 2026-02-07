# agent/mock_ai.py

def mock_vision(step):
    if step == 1:
        return {
            "screen_type": "home",
            "elements": ["LOGIN", "CONTACT US"],
            "error_text": None
        }
    if step == 2:
        return {
            "screen_type": "login",
            "elements": ["EMAIL_FIELD", "PASSWORD_FIELD", "SUBMIT"],
            "error_text": None
        }
    if step == 3:
        return {
            "screen_type": "error",
            "elements": ["ERROR_POPUP"],
            "error_text": "Invalid credentials"
        }
