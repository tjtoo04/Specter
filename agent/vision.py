import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from google import genai
from google.genai import types
from google.genai.types import Content, Part
from typing import Any, List, Tuple
import time
from pathlib import Path
import json
import re
from prompts import MYSTERY_SHOPPER_SYSTEM_PROMPT, INITIAL_TASK_PROMPT

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

SCREEN_WIDTH = 375
SCREEN_HEIGHT = 812

playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
context = browser.new_context(viewport={"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT})
page = context.new_page()

def extract_json_from_text(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Look for JSON within code blocks or plain text
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```|(\{[^{}]*"screen_type"[^{}]*\})'
        matches = re.findall(json_pattern, text, re.DOTALL)
        for match in matches:
            json_str = match[0] or match[1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                continue
        return None

def denormalize_x(x: int, screen_width: int) -> int:
    """Convert normalized x coordinate (0-1000) to actual pixel coordinate."""
    return int(x / 1000 * screen_width)

def denormalize_y(y: int, screen_height: int) -> int:
    """Convert normalized y coordinate (0-1000) to actual pixel coordinate."""
    return int(y / 1000 * screen_height)

def execute_function_calls(candidate, page, screen_width, screen_height):
    results = []
    function_calls = []
    for part in candidate.content.parts:
        if part.function_call:
            function_calls.append(part.function_call)

    for function_call in function_calls:
        action_result = {}
        fname = function_call.name
        args = function_call.args
        print(f"  -> Executing: {fname}")

        try:
            if fname == "open_web_browser":
                pass # Already open
            elif fname == "click_at":
                actual_x = denormalize_x(args["x"], screen_width)
                actual_y = denormalize_y(args["y"], screen_height)
                page.mouse.click(actual_x, actual_y)
            elif fname == "type_text_at":
                actual_x = denormalize_x(args["x"], screen_width)
                actual_y = denormalize_y(args["y"], screen_height)
                text = args["text"]
                press_enter = args.get("press_enter", False)

                page.mouse.click(actual_x, actual_y)
                # Simple clear (Command+A, Backspace for Mac)
                page.keyboard.press("Meta+A")
                page.keyboard.press("Backspace")
                page.keyboard.type(text)
                if press_enter:
                    page.keyboard.press("Enter")
            else:
                print(f"Warning: Unimplemented or custom function {fname}")

            # Wait for potential navigations/renders
            page.wait_for_load_state(timeout=5000)
            time.sleep(1)

        except Exception as e:
            print(f"Error executing {fname}: {e}")
            action_result = {"error": str(e)}

        results.append((fname, action_result))

    return results

def get_function_responses(page, results):
    screenshot_bytes = page.screenshot(type="png")
    current_url = page.url
    function_responses = []
    
    # Save screenshot to evidence/screenshots folder
    screenshot_dir = Path("evidence/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
    screenshot_path = screenshot_dir / f"screenshot_{timestamp}.png"
    with open(screenshot_path, "wb") as f:
        f.write(screenshot_bytes)
    print(f"  Saved: {screenshot_path}")
    
    for name, result in results:
        response_data = {"url": current_url, "screenshot_path": str(screenshot_path)}
        response_data.update(result)
        function_responses.append(
            types.FunctionResponse(
                name=name,
                response=response_data,
                parts=[types.FunctionResponsePart(
                        inline_data=types.FunctionResponseBlob(
                            mime_type="image/png",
                            data=screenshot_bytes))
                ]
            )
        )
    return function_responses

try:
  # Go to initial page
  page.goto("https://specterai.duckdns.org/")

  # Configure the model with system prompt
  config = types.GenerateContentConfig(
    tools=[types.Tool(computer_use=types.ComputerUse(
            environment=types.Environment.ENVIRONMENT_BROWSER
        ))],
        thinking_config=types.ThinkingConfig(include_thoughts=True),
        system_instruction=MYSTERY_SHOPPER_SYSTEM_PROMPT,
  )

  initial_screenshot = page.screenshot(type="png")
  USER_PROMPT = INITIAL_TASK_PROMPT
  print(f"Goal: Mystery Shopping Assessment")
  print(f"Instructions: {USER_PROMPT[:100]}...")

  contents = [
        Content(role="user", parts=[
            Part(text=USER_PROMPT),
            Part.from_bytes(data=initial_screenshot, mime_type='image/png')
        ])
    ]
  
  # Store all screen analyses
  screen_analyses = []
  last_screen_type = None
  screen_repeat_count = 0
  
  turn_limit = 15
  for i in range(turn_limit):
      turn_start_time = time.time()
      pending_jsons = []
      print(f"\n--- Turn {i+1} ---")
      print("Thinking...")
      response = client.models.generate_content(
          model='gemini-2.5-computer-use-preview-10-2025',
          contents=contents,
          config=config,
      )

      candidate = response.candidates[0]
      contents.append(candidate.content)

      # Print any text responses (including JSON analysis)
      text_parts = [part.text for part in candidate.content.parts if part.text]
      if text_parts:
          print("\n" + "="*60)
          print("AGENT RESPONSE:")
          print("="*60)
          for text in text_parts:
              print(text)
              # Extract and store JSON analysis
              json_data = extract_json_from_text(text)
              if json_data:
                  json_data['turn'] = i + 1
                  json_data['url'] = page.url
                  json_data['timestamp'] = int(time.time())
                  pending_jsons.append(json_data)
          print("="*60 + "\n")

      function_calls = [part.function_call for part in candidate.content.parts if part.function_call]
      attempts = len(function_calls)
      last_action = function_calls[-1].name if function_calls else None
      has_function_calls = attempts > 0
      if not has_function_calls:
          turn_duration = max(0, round(time.time() - turn_start_time))
          for json_data in pending_jsons:
              screen_type = json_data.get('screen_type')
              if screen_type and screen_type == last_screen_type:
                  screen_repeat_count += 1
              else:
                  screen_repeat_count = 1
                  last_screen_type = screen_type
              json_data['time_on_screen'] = turn_duration
              json_data['attempts'] = attempts
              json_data['last_action'] = last_action
              json_data['screen_repeat_count'] = screen_repeat_count
              screen_analyses.append(json_data)
              print(f"\n✓ Captured analysis for: {json_data.get('screen_type', 'unknown')}")
          print("\nAgent finished exploration.")
          break

      print("Executing actions...")
      results = execute_function_calls(candidate, page, SCREEN_WIDTH, SCREEN_HEIGHT)

      print("Capturing state...")
      function_responses = get_function_responses(page, results)

      contents.append(
          Content(role="user", parts=[Part(function_response=fr) for fr in function_responses])
      )

      turn_duration = max(0, round(time.time() - turn_start_time))
      for json_data in pending_jsons:
          screen_type = json_data.get('screen_type')
          if screen_type and screen_type == last_screen_type:
              screen_repeat_count += 1
          else:
              screen_repeat_count = 1
              last_screen_type = screen_type
          json_data['time_on_screen'] = turn_duration
          json_data['attempts'] = attempts
          json_data['last_action'] = last_action
          json_data['screen_repeat_count'] = screen_repeat_count
          screen_analyses.append(json_data)
          print(f"\n✓ Captured analysis for: {json_data.get('screen_type', 'unknown')}")
  
  # Print summary of collected analyses
  print("\n" + "="*60)
  print(f"SUMMARY: Collected {len(screen_analyses)} screen analyses")
  print("="*60)
  for analysis in screen_analyses:
      print(f"  - Turn {analysis['turn']}: {analysis.get('screen_type', 'unknown')} (confidence: {analysis.get('confidence', 0):.2f})")
  print("="*60)

finally:
    # Cleanup
    print("\nClosing browser...")
    browser.close()
    playwright.stop()
    print(screen_analyses)
