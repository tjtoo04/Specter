from controller.appium_driver import get_driver
from controller.actions import scroll, tap, type_text
import time

# STEP 0 — System boot
driver = get_driver()

# STEP 1 — Choose test case
TEST_CASE = 1   # change to 1, 2, or 3

# =========================
# TEST CASE 1
# Scroll → Login → Cart
# =========================
if TEST_CASE == 1:
    print("Running Test Case 1")

    scroll(driver, 931, 820, 80, 820)
    tap(driver, "LOGIN")
    tap(driver, "LOGIN")  # retry
    tap(driver, "CART")

# =========================
# TEST CASE 2
# Contact Us → Fill Form → Submit
# =========================
elif TEST_CASE == 2:
    print("Running Test Case 2")

    scroll(driver, 820, 860, 105, 860)
    tap(driver, "CONTACT_US")

    type_text(driver, "NAME", "Luis Infante")
    type_text(driver, "EMAIL", "adress@domain.com")
    type_text(driver, "SUBJECT", "Inquiry")
    type_text(driver, "MESSAGE", "Test submission")

    tap(driver, "SUBMIT")

# =========================
# TEST CASE 3
# New Flavours → Buy
# =========================
elif TEST_CASE == 3:
    print("Running Test Case 3")

    tap(driver, "NEW_FLAVOURS")
    tap(driver, "BUY")

# STEP X — End
time.sleep(3)
driver.quit()
print("Test completed")
