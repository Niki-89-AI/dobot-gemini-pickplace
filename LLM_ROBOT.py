import os
import sys
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from call_function import call_function, available_functions
from Robot_Tools.Robot_Motion_Tools import device_close

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    MODEL_ID = "gemini-2.5-flash"
    verbose = False
    max_iter = 20

    # Optional initial prompt from CLI
    initial_prompt = None
    if len(sys.argv) >= 2:
        initial_prompt = sys.argv[1]
    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose = True
   
   
    system_prompt = """
    You control a physical Dobot robot arm that picks and places colored blocks.
    You MUST use the provided tools for every action. Never simulate or assume an action happened.

    === REQUIRED EXECUTION ORDER ===
    1. Connect to robot  →  get_dobot_device (use the default port — do not ask the user for it)
    2. Home the robot    →  move_to_home
    3. Capture scene     →  capture_scene_with_detection (this captures the image AND detects blocks in one step)
    4. Summarize detected blocks to the user (use exact labels like "red1", "blue2")
    5. Execute task      →  pick_and_place_block
    6. Home after done   →  move_to_home

    === SAFETY RULES ===
    - Always home the robot before AND after any pick-and-place operation.
    - Never skip the scene capture step — always call capture_scene_with_detection before moving.
    - If a requested block label is not found in the detection results, tell the user and stop. Do not guess positions.
    - If a tool returns an error, report it to the user and do not continue.
    - Never chain multiple pick-and-place calls without homing in between.

    === BEHAVIOR ===
    - If the task is already clear from the initial prompt, proceed immediately without asking for confirmation.
    - Use the default serial port — never prompt the user for port selection.
    - After completing the task, briefly summarize what was done.

    === BLOCK LABELS ===
    - Use only exact labels returned by capture_scene_with_detection (e.g. "red1", "blue1", "green2").
    - Never use generic names like "the red block" or "block 1".

    === PLACEMENT RELATIONS ===
    "on top of"   → placement_type="on_top"
    "left of"     → placement_type="beside", direction="left"
    "right of"    → placement_type="beside", direction="right"
    "in front of" → placement_type="beside", direction="front"
    "behind"      → placement_type="beside", direction="back"

    === INCOMPLETE REQUESTS ===
    If the user does not specify both a source block and a target block and a placement relation, ask for the missing information before proceeding.
    """


    print("\n================ SYSTEM PROMPT ================\n")
    print(system_prompt.strip(), "\n")

    # Conversation history (user + assistant + tool messages)
    messages = []

    # If we got an initial CLI prompt, use it as the first user message
    if initial_prompt:
        print("\n================ USER PROMPT (CLI) ================\n")
        print(initial_prompt)
        messages.append(
            types.Content(role="user", parts=[types.Part(text=initial_prompt)])
        )
    else:
        # Otherwise, ask interactively for the first input
        user_text = input("\nYou (type 'quit' to exit): ").strip()
        if user_text.lower() in {"quit", "exit", "q"}:
            print("Exiting.")
            return
        messages.append(
            types.Content(role="user", parts=[types.Part(text=user_text)])
        )

    config = types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt
    )

    func_count = 0

    # ================= INTERACTIVE CONVERSATION LOOP =================
    while True:
        # For each user message, allow multiple tool/model turns
        for i in range(max_iter):
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=messages,
                config=config
            )

            # ------------ MODEL TEXT ------------
            if response.text:
                print("\n================ MODEL TEXT RESPONSE ================\n")
                print(response.text)

            if verbose and response.usage_metadata:
                print(f'prompt = {messages[-1].parts[0].text if messages else ""}')
                print(f'Response = {response.text}')
                print(f'Prompt Token = {response.usage_metadata.prompt_token_count}')
                print(f'Response Token = {response.usage_metadata.candidates_token_count}')

            # Add assistant content to history
            if response.candidates:
                for candidate in response.candidates:
                    if candidate and candidate.content:
                        messages.append(candidate.content)

            # ------------ TOOL CALLS ------------
            if response.function_calls:
                for function_call_part in response.function_calls:
                    func_count += 1
                    fname = getattr(function_call_part, "name", None)
                    fargs = getattr(function_call_part, "args", {})

                    print(f"\n================ FUNCTION CALL #{func_count} ================\n")
                    print(f"Function name: {fname}")
                    print("Arguments (tool prompt):")
                    try:
                        print(json.dumps(fargs, indent=2))
                    except TypeError:
                        print(fargs)

                    # Run tool
                    result = call_function(function_call_part, verbose=True)

                    print(f"\n================ FUNCTION RESULT #{func_count} ================\n")
                    print(result)

                    # Append tool result so the model can see it next iteration
                    messages.append(result)

                # continue inner for-loop to let the model react to the tool results
                continue

            # ---------- NO FUNCTION CALLS -> END OF THIS TURN ----------
            break  # break out of the max_iter loop; ready for next user input

        # ================= ASK FOR NEXT USER INPUT =================
        print("\n================ AWAITING USER INPUT (type 'quit' to exit) ================\n")
        user_text = input("You: ").strip()

        if user_text.lower() in {"quit", "exit", "q"}:
            print("Closing robot connection before exit...")
            try:
                result = device_close()
                print(result)
            except Exception as e:
                print(f"Error closing device: {e}")

            print("Exiting interactive session.")
            break
        print("\n================ USER PROMPT ================\n")
        print(user_text)

        # Add new user message and loop again
        messages.append(
            types.Content(role="user", parts=[types.Part(text=user_text)])
        )

if __name__ == "__main__":
    main()

