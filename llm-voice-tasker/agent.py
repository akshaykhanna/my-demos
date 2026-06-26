import json
import urllib.request
import urllib.error
import sys

from tools import TOOLS
from voice import listen_for_command

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma2:2b"

SYSTEM_PROMPT = """
You are a Windows System Assistant. You help the user open software and find download links.
You can execute actions on the laptop by outputting a tool call formatted exactly like this:

Action: tool_name(argument)

Available Tools:
- open_application(app_name): Launches the software. Example: Action: open_application("Spotify")
- search_download_page(app_name): Opens a browser tab search for downloading the software if it is missing. Example: Action: search_download_page("Zoom")

Instructions:
1. First, try to open the requested application.
2. If the tool response says "Error: Application ... is not installed", you MUST call search_download_page to help the user download it.
3. Once completed, answer the user beginning with:
Answer: <your final confirmation response>
"""

def query_llm(messages):
    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.0}
    }
    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8")).get("message", {}).get("content", "")
    except urllib.error.URLError as e:
        print(f"\n[Error] Ollama connection failed. Make sure Ollama app is running: {e}")
        sys.exit(1)

def run_agent(user_query):
    if not user_query:
        print("No command received.")
        return

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]
    
    for step in range(5):
        response = query_llm(messages).strip()
        
        if response.startswith("Action:"):
            try:
                # Parse: Action: tool_name(arg)
                action_str = response[7:].strip()
                tool_name, arg_str = action_str.split("(", 1)
                arg = arg_str.rsplit(")", 1)[0].strip().strip('"').strip("'")
                
                # Execute tool
                observation = TOOLS[tool_name](arg)
                print(f"  [Observation] {observation}")
                
                # Update context
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"Observation: {observation}"})
            except Exception as e:
                observation = f"Error parsing tool syntax: {e}"
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"Observation: {observation}"})
                
        elif response.startswith("Answer:"):
            print(f"\nAgent: {response[7:].strip()}")
            return
        else:
            print(f"\nAgent: {response}")
            return
            
    print("\nAgent: Exceeded maximum steps.")

if __name__ == "__main__":
    print("=" * 60)
    print(" Local LLM Tasker Agent ".center(60, "="))
    print("=" * 60)
    print("Choose your input mode:")
    print("  [1] Text Chat (type commands directly)")
    print("  [2] Voice Command (speak into your microphone)")
    print("=" * 60)
    
    choice = input("\nSelect mode (1 or 2): ").strip()
    
    if choice == "2":
        # Voice Command Mode
        spoken_command = listen_for_command()
        if spoken_command:
            run_agent(spoken_command)
    else:
        # Interactive Text Chat Mode
        print("\nText Chat Mode Activated. Type your request (e.g., 'Open Chrome').")
        print("Type 'exit' or 'quit' to end the session.")
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit"]:
                    print("\nGoodbye!")
                    break
                run_agent(user_input)
            except KeyboardInterrupt:
                print("\nSession ended. Goodbye!")
                break
