from controller.appium_driver import get_driver
from controller.actions import execute_action

from agent.decision import decide_next_action
from agent.vision import analyze_screen

from state.tracker import StateTracker
from state.frictions import detect_friction


MAX_STEPS = 15   # hard cap for demo


def run_agent_loop(test_case: str):
    print(f"\n▶ Running test case: {test_case}")

    driver = get_driver()
    tracker = StateTracker()

    step_index = 0

    try:
        while step_index < MAX_STEPS:
            print(f"\n--- Loop step {step_index} ---")

            # STEP 1 — Decide next intent
            intent = decide_next_action(test_case, step_index)

            if intent is None:
                print("✅ Flow completed normally.")
                break

            # STEP 2 — Execute action
            result = execute_action(driver, intent)

            # STEP 3 — Screenshot
            screenshot_path = f"evidence/screenshots/step_{step_index}.png"
            driver.save_screenshot(screenshot_path)

            # STEP 4 — Vision
            vision_output = analyze_screen(screenshot_path)

            # STEP 5 — State update
            state_snapshot = tracker.update(
                vision_output=vision_output,
                action_result=result
            )
            tracker.set_last_action(intent)

            # 🔒 NORMALISE STATE KEYS (match detect_friction expectations)
            state_snapshot = {
            "current_screen_id": state_snapshot.get("Current_screen_id"),
            "time_on_screen": state_snapshot.get("time_on_Screen", 0),
            "attempts_on_screen": state_snapshot.get("Attempts_on_screen", 0),
            "screen_repeat_count": state_snapshot.get("Screen_repeat_count", 0),
            "history": state_snapshot.get("history", []),
            "action_succeeded": state_snapshot.get("action_succeeded", False),
            
            }


            

            print("State snapshot:", state_snapshot)

            # STEP 6 — Friction detection
            is_stuck, friction_type = detect_friction(state_snapshot)

            # STEP 7 — If friction detected → PRINT + STOP
            if is_stuck:
                print("\n⚠️ FRICTION DETECTED")
                print("Type:", friction_type)

                diagnosis = {
                    "issue_type": "UX Friction",
                    "severity": "P2",
                    "root_cause": f"Detected friction: {friction_type}",
                    "suggested_team": "Frontend",
                }

                print("\n🧠 DIAGNOSIS")
                for k, v in diagnosis.items():
                    print(f"{k}: {v}")

                print("\n🛑 Agent stopping after detecting issue.")
                break

            step_index += 1

        else:
            print("\n⏹ Max steps reached without friction.")

    finally:
        driver.quit()
        print("\n🧹 Driver closed.")
        print("🏁 Agent loop finished.\n")


# -------------------------
# ENTRY POINT (MENU)
# -------------------------
if __name__ == "__main__":

    print("""
Select test case:
1 - Login button issue
2 - Contact Us form issue
3 - Buy flow issue
""")

    choice = input("Enter choice: ").strip()

    TEST_CASES = {
        "1": "login",
        "2": "contact",
        "3": "buy"
    }

    if choice not in TEST_CASES:
        print("❌ Invalid choice")
        exit(1)

    run_agent_loop(TEST_CASES[choice])
