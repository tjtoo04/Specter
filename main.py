from controller.appium_driver import get_driver
from controller.actions import execute_action

from agent.decision import decide_next_action
from agent.vision import analyze_screen
# from agent.diagnosis import diagnose   # ❌ COMMENTED (Gemini disabled)

from state.tracker import StateTracker
from state.frictions import detect_friction

#from evidence.collector import package_evidence
#1
# from alerts.slack import send_alert


MAX_STEPS = 15   # safety cap for demo


def run_agent_loop(test_case):
    print(f"\n Running test case: {test_case}")

    driver = get_driver()
    tracker = StateTracker()

    execution_steps = []
    step_index = 0

    while step_index < MAX_STEPS:
        print(f"\n--- Loop step {step_index} ---")

        # STEP 4 — Decide intent (YOU)
        intent = decide_next_action(test_case, step_index)

        if intent is None:
            print(" Flow completed normally.")
            break

        # STEP 5 — Execute action (Appium)
        result = execute_action(driver, intent)

        # STEP 2A — Screenshot (still OK, cheap)
        screenshot_path = f"evidence/screenshots/step_{step_index}.png"
        driver.save_screenshot(screenshot_path)

        # STEP 2B — Vision (TEMP placeholder)
        vision_output = analyze_screen(screenshot_path)

        # STEP 3 — State update
        state_snapshot = tracker.update(
            vision_output=vision_output,
            action_result=result
        )
        tracker.set_last_action(intent)

        # STEP 7 — Friction detection
        is_stuck, friction_type = detect_friction(state_snapshot)


        execution_steps.append({
            "step": step_index,
            "intent": intent,
            "action_result": result,
            "vision": vision_output,
            "state": state_snapshot,
            "friction": friction_type
        })

        # STEP 8 — Diagnosis (❌ Gemini skipped)
        if is_stuck:
            print("⚠️ Friction detected:", friction_type)

            # 🔒 TEMP MOCK DIAGNOSIS (SAFE)
            diagnosis = {
                "issue_type": "UX Friction",
                "severity": "P2",
                "root_cause": f"Friction detected: {friction_type}",
                "suggested_team": "Frontend"
            }

            payload = {
                "test_case": test_case,
                "execution": execution_steps,
                "diagnosis": diagnosis
            }

            # STEP 9 — Evidence (CINDY)
            package_evidence(payload)

            # STEP 10 — Alert (CINDY)
            send_alert(payload)

            break

        step_index += 1

    driver.quit()
    print(" Agent loop finished.\n")


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
        print(" Invalid choice")
        exit(1)

    run_agent_loop(TEST_CASES[choice])
