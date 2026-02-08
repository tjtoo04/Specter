import time

COORDINATES = {
    # Test Case 1
    "LOGIN": (600, 458),
    "CART": (890, 473),

    # Test Case 2
    "CONTACT_US": (486, 400),
    "NAME": (500, 1214),
    "EMAIL": (577, 1473),
    "SUBJECT": (486, 1690),
    "MESSAGE": (439, 1930),
    "SUBMIT": (401, 2146),

    # Test Case 3
    "NEW_FLAVOURS": (430, 2282),
    "BUY": (609, 1852),
}

def execute_action(driver, intent):
    start = time.time()

    try:
        action = intent["action"]
        target = intent.get("target")

        if action == "tap":
            x, y = COORDINATES[target]
            driver.tap([(x, y)])

        elif action == "type":
            x, y = COORDINATES[target]
            driver.tap([(x, y)])
            time.sleep(0.5)
            driver.execute_script(
                "mobile: type",
                {"text": intent["text"]}
            )

        elif action == "scroll":
            driver.swipe(950, 820, 52, 803, 600)

        elif action == "wait":
            time.sleep(intent.get("seconds", 2))

        return {
            "success": True,
            "execution_time": round(time.time() - start, 2),
            "action": intent
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "execution_time": round(time.time() - start, 2),
            "action": intent
        }
