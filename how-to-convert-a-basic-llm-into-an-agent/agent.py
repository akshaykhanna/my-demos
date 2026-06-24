import os
import json
import shutil
from ollama import Client

# --- Configuration ---
TARGET_DIRECTORY = "test_files"  # The directory the agent will organize
OLLAMA_MODEL = "gemma:2b"        # The LLM model to use (ensure you have it pulled via `ollama pull gemma:2b`)
OLLAMA_HOST = "http://localhost:11434" # Ollama server address

# --- LLM Client Setup ---
try:
    # Initialize the Ollama client to connect to the local Ollama server
    ollama_client = Client(host=OLLAMA_HOST)
    # Attempt a basic call to verify connection and model availability
    # This will list available models, confirming Ollama is reachable.
    ollama_client.list()
    print(f"Connected to Ollama at {OLLAMA_HOST}")
except Exception as e:
    print(f"Error connecting to Ollama: {e}. Please ensure Ollama is running and accessible.")
    print("Refer to README.md for setup instructions, especially `ollama pull gemma:2b`.")
    exit(1)

# --- Tool Functions (Agent's 'Hands') ---
# These functions allow the agent to interact with its environment (the file system).

def get_files_in_directory(directory_path):
    """
    Lists all files (excluding directories) in the specified directory.
    This is one of the agent's 'observation' tools, allowing it to 'see' the environment.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        print(f"Created target directory: {directory_path}")
        return []
    
    files = []
    for entry in os.listdir(directory_path):
        full_path = os.path.join(directory_path, entry)
        if os.path.isfile(full_path):
            files.append(entry)
    return files

def create_directory_if_not_exists(directory_path):
    """
    Creates a directory if it doesn't already exist.
    This is an agent's 'action' tool, allowing it to modify the environment.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")

def move_file(source_path, destination_path):
    """
    Moves a file from its source path to a new destination path.
    This is another agent's 'action' tool.
    """
    try:
        shutil.move(source_path, destination_path)
        print(f"Moved: '{os.path.basename(source_path)}' to '{os.path.dirname(destination_path)}'")
        return True
    except FileNotFoundError:
        print(f"Error: Source file not found at '{source_path}'")
        return False
    except Exception as e:
        print(f"Error moving file '{source_path}': {e}")
        return False

# --- Agent Core Logic ---

def get_llm_suggestions(files_in_dir, target_dir):
    """
    Communicates with the LLM to get file categorization suggestions.
    This is the agent's 'thinking' or 'planning' component. The LLM is stateless,
    so the agent provides all necessary context (the list of files) in each call.
    """
    if not files_in_dir:
        return []

    # The prompt is carefully engineered to provide the LLM with context,
    # task instructions, and a strict output format (JSON) to ensure reliable parsing.
    system_prompt = f"""
    You are an AI file organization assistant. Your task is to categorize files in a given directory
    and suggest new paths for them. The categorization should be logical and common (e.g., 'Documents', 'Images', 'Archives', 'Reports', 'Code', 'Notes').

    For each file provided, determine a suitable category. Then, suggest a new full path for the file
    within the '{target_dir}' directory, e.g., '{target_dir}/<Category>/<filename>'.

    Provide your suggestions as a JSON array of objects. Each object MUST have the following keys:
    - 'file_name': The original name of the file (e.g., 'report_q1_2023.pdf').
    - 'current_path': The full original path of the file (e.g., '{target_dir}/report_q1_2023.pdf').
    - 'suggested_category': The category you determined for the file (e.g., 'Reports').
    - 'new_path': The full suggested new path for the file (e.g., '{target_dir}/Reports/report_q1_2023.pdf').
    - 'reason': A brief explanation (1-2 sentences) for your categorization.

    Ensure the output is valid JSON and only contains the JSON array. Do not include any other text or markdown outside the JSON.
    """

    user_message = f"Here are the files in the '{target_dir}' directory that need organizing:\n{json.dumps(files_in_dir, indent=2)}\n\nPlease provide your categorization suggestions in the specified JSON format." # Pass full paths to LLM.

    print("\n--- Agent Thinking (Calling LLM) ---")
    try:
        response = ollama_client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message},
            ],
            # Lower temperature for more consistent and less creative categorization
            options={"temperature": 0.3}
        )
        llm_response_content = response['message']['content']
        # Uncomment the line below for debugging the raw LLM output
        # print(f"Raw LLM Response:\n{llm_response_content}\n")

        # Robust JSON parsing: LLMs can sometimes add introductory text or minor formatting issues.
        try:
            # Find the actual JSON array within the response content
            json_start = llm_response_content.find('[')
            json_end = llm_response_content.rfind(']')
            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_string = llm_response_content[json_start : json_end + 1]
                suggestions = json.loads(json_string)
            else:
                raise ValueError("Could not find a valid JSON array in LLM response.")
            
            # Basic validation of the LLM's output structure
            if not isinstance(suggestions, list):
                raise ValueError("LLM response is not a JSON list.")
            
            # Further validate and potentially correct missing keys (robustness)
            for i, s in enumerate(suggestions):
                if not all(k in s for k in ["file_name", "current_path", "suggested_category", "new_path", "reason"]):
                    print(f"Warning: LLM suggestion {i+1} missing expected keys: {s}")
                    # Attempt to infer missing paths if file_name and category are present
                    if 'file_name' in s and 'current_path' not in s:
                        s['current_path'] = os.path.join(target_dir, s['file_name'])
                    if 'file_name' in s and 'suggested_category' in s and 'new_path' not in s:
                        s['new_path'] = os.path.join(target_dir, s['suggested_category'], s['file_name'])
                        
            print("LLM suggestions received and parsed.")
            return suggestions
        except json.JSONDecodeError as jde:
            print(f"Error parsing LLM JSON response: {jde}")
            print(f"Problematic content:\n{llm_response_content}")
            return []
        except ValueError as ve:
            print(f"Error in LLM response structure: {ve}")
            print(f"Problematic content:\n{llm_response_content}")
            return []

    except Exception as e:
        print(f"Error communicating with Ollama or LLM model: {e}")
        print(f"Please ensure the model '{OLLAMA_MODEL}' is pulled (e.g., `ollama pull {OLLAMA_MODEL}`)")
        print(f"and the Ollama server is running at {OLLAMA_HOST}.")
        return []

def confirm_and_execute_actions(actions):
    """
    Presents proposed actions to the user for confirmation and then executes them.
    This demonstrates the 'human-in-the-loop' pattern, crucial for agent safety and control.
    """
    if not actions:
        print("No valid actions to perform.")
        return

    print("\n--- Proposed File Organization Actions ---")
    for i, action in enumerate(actions):
        print(f"\n{i+1}. File: '{action.get('file_name', 'N/A')}'")
        print(f"   Current Path: {action.get('current_path', 'N/A')}")
        print(f"   Suggested Category: {action.get('suggested_category', 'N/A')}")
        print(f"   New Path: {action.get('new_path', 'N/A')}")
        print(f"   Reason: {action.get('reason', 'No reason provided.')}")

    while True:
        confirmation = input("\nDo you want to execute these actions? (yes/no): ").lower().strip()
        if confirmation in ['yes', 'y']:\
            print("\n--- Executing Actions ---")
            for action in actions:
                # Ensure the target category directory exists before moving the file
                category_dir = os.path.dirname(action['new_path'])
                create_directory_if_not_exists(category_dir)
                move_file(action['current_path'], action['new_path'])
            print("\nActions executed successfully!")
            break
        elif confirmation in ['no', 'n']:\
            print("Actions cancelled by user.")
            break
        else:
            print("Invalid input. Please type 'yes' or 'no'.")

# --- Main Agent Loop (Simplified for Demo) ---

def run_file_organizer_agent():
    """
    The main function that orchestrates the agent's behavior.
    This simulates the agent's 'brain' controlling its perception, planning, and action loop.
    """
    print(f"Starting File Organizer Agent for directory: '{TARGET_DIRECTORY}'")
    print("--------------------------------------------------")

    # Agent's Observation (Perception)
    # The agent uses its 'get_files_in_directory' tool to perceive the environment.
    initial_files = get_files_in_directory(TARGET_DIRECTORY)

    # If no files are found initially, create some dummy files for a smooth demonstration.
    if not initial_files:
        print(f"No files found in '{TARGET_DIRECTORY}' to organize. Creating dummy files for demo...")
        create_dummy_files(TARGET_DIRECTORY)
        initial_files = get_files_in_directory(TARGET_DIRECTORY) # Re-observe after creating files
        if not initial_files:
            print("Failed to create dummy files or still no files found. Exiting.")
            return

    print(f"\nFound {len(initial_files)} files in '{TARGET_DIRECTORY}':")
    for f in initial_files:
        print(f" - {f}")

    # Agent's Planning (LLM's 'Thinking')
    # The LLM is stateless, so the agent explicitly provides the current observed state
    # (list of files with their full paths) as context in the prompt.
    current_full_file_paths = [os.path.join(TARGET_DIRECTORY, f) for f in initial_files]
    suggestions = get_llm_suggestions(current_full_file_paths, TARGET_DIRECTORY)

    # Agent's Action (with Human-in-the-Loop Confirmation)
    if suggestions:
        # Filter out invalid or redundant suggestions to make the agent more robust.
        valid_suggestions = []
        for s in suggestions:
            current_path_for_action = s.get('current_path')
            new_path_for_action = s.get('new_path')
            file_name = s.get('file_name', 'N/A')
            
            # Check if the file still exists, if the suggested path is different,
            # and if the new path is within the target directory to prevent accidental moves.
            if (current_path_for_action and new_path_for_action and
                os.path.exists(current_path_for_action) and
                os.path.normpath(current_path_for_action) != os.path.normpath(new_path_for_action) and
                os.path.normpath(new_path_for_action).startswith(os.path.normpath(TARGET_DIRECTORY))):
                valid_suggestions.append(s)
            else:
                print(f"Skipping invalid/redundant suggestion for '{file_name}'. (Current: {current_path_for_action}, New: {new_path_for_action})")

        if valid_suggestions:
            # The agent uses its 'confirm_and_execute_actions' tool, which involves human input.
            confirm_and_execute_actions(valid_suggestions)
        else:
            print("No valid actions to perform based on LLM suggestions or files are already organized.")
    else:
        print("No categorization suggestions generated by the LLM.")

    print("\n--------------------------------------------------")
    print("Agent run finished.")

def create_dummy_files(directory):
    """
    Helper function to create some dummy files for demonstration purposes.
    These files simulate an unorganized directory.
    """
    os.makedirs(directory, exist_ok=True)
    dummy_files_content = {
        "report_q1_2024.pdf": "This is a dummy Q1 2024 financial report.",
        "meeting_notes_2024-03-20.txt": "Notes from today's team meeting.",
        "project_plan_v2.docx": "Updated project plan document.",
        "holiday_pic_beach.jpg": "A lovely beach photo from vacation.",
        "recipe_pasta.md": "My favorite pasta recipe.",
        "source_code_main.py": "Python script for a small utility.",
        "archive.zip": "A compressed archive of old documents.",
        "invoice_2023_12.pdf": "December 2023 invoice."
    }
    
    print(f"Creating dummy files in '{directory}'...")
    for filename, content in dummy_files_content.items():
        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write(content)
            print(f" - Created '{filename}'")
        else:
            print(f" - '{filename}' already exists, skipping creation.")


if __name__ == "__main__":
    # Pre-run cleanup: Offer to remove the test_files directory if it looks like
    # it contains categorized subdirectories from a previous run. This ensures a fresh demo.
    if os.path.exists(TARGET_DIRECTORY):
        print(f"Checking '{TARGET_DIRECTORY}' for existing categories...")
        contains_subdirs = any(os.path.isdir(os.path.join(TARGET_DIRECTORY, d)) for d in os.listdir(TARGET_DIRECTORY))
        if contains_subdirs:
            print(f"'{TARGET_DIRECTORY}' contains subdirectories, suggesting a clean start for the demo.")
            if input(f"Do you want to remove '{TARGET_DIRECTORY}' and its contents to start fresh? (y/n): ").lower() == 'y':
                print(f"Removing '{TARGET_DIRECTORY}'...")
                shutil.rmtree(TARGET_DIRECTORY)
                print(f"'{TARGET_DIRECTORY}' removed.")
            else:
                print("Keeping existing directory structure. Agent will work with current files.")

    # Start the agent's main execution flow
    run_file_organizer_agent()
