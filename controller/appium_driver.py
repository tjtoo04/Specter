from appium import webdriver
from appium.options.android import UiAutomator2Options
import time

URL = "https://penny-juice.com/#slide-2"

def get_driver():
    options = UiAutomator2Options()

    options.platform_name = "Android"
    options.device_name = "Android Emulator"
    options.automation_name = "UiAutomator2"

    # Launch Chrome
    options.app_package = "com.android.chrome"
    options.app_activity = "com.google.android.apps.chrome.Main"
    options.arguments = ["--disable-fre", "--no-first-run"]

    driver = webdriver.Remote(
        command_executor="http://127.0.0.1:4723",
        options=options
    )

    time.sleep(3)

    # Load target website
    driver.get(URL)
    time.sleep(3)

    return driver
