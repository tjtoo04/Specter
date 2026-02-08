def decide_next_action(test_case, step_index):
    """
    Returns the next INTENT only
    """

    flows = {
        "login": [
            {"action": "scroll"},
            {"action": "tap", "target": "LOGIN"},
            {"action": "tap", "target": "LOGIN"},
            {"action": "tap", "target": "LOGIN"},
        ],

        "contact": [
            {"action": "scroll"},
            {"action": "tap", "target": "CONTACT_US"},
            {"action": "type", "target": "NAME", "text": "Luis Infante"},
            {"action": "type", "target": "EMAIL", "text": "adress@domain.com"},
            {"action": "type", "target": "SUBJECT", "text": "Inquiry"},
            {"action": "type", "target": "MESSAGE", "text": "Test message"},
            {"action": "tap", "target": "SUBMIT"},
        ],

        "buy": [
            {"action": "tap", "target": "NEW_FLAVOURS"},
            {"action": "tap", "target": "BUY"},
        ]
    }

    flow = flows[test_case]

    if step_index >= len(flow):
        return None

    return flow[step_index]
