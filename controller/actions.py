import time

COORDINATES = {
    # Test Case 1
    "LOGIN": (600, 458),
    "CART": (890, 473),

    # Test Case 2
    "CONTACT_US": (381, 1300),
    "NAME": (500, 1214),
    "EMAIL": (577, 1473),
    "SUBJECT": (486, 1690),
    "MESSAGE": (439, 1930),
    "SUBMIT": (401, 2146),

    # Test Case 3
    "NEW_FLAVOURS": (199, 2276),
    "BUY": (609, 1852),
}

def scroll(driver, start_x, start_y, end_x, end_y, duration=500):
    driver.swipe(start_x, start_y, end_x, end_y, duration)
    time.sleep(1)

def tap(driver, target):
    x, y = COORDINATES[target]
    driver.tap([(x, y)])
    time.sleep(1)

def type_text(driver, target, text):
    x, y = COORDINATES[target]
    driver.tap([(x, y)])
    time.sleep(0.5)
    driver.execute_script("mobile: type", {"text": text})
    time.sleep(1)
