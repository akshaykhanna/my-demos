A basic LLM (like Gemma or Llama 3 via Ollama) is inherently stateless. This means each interaction with it is fresh, without memory of past queries or the ability to perform actions in the real world. To turn an LLM into an "Agent," we need to wrap it with additional capabilities:

1.  **Loops:** To enable continuous observation, thought, and action cycles.
2.  **Memory:** To retain information across interactions, building context over time.
3.  **Tools:** Functions or APIs that the agent can "call" to interact with its environment (e.g., read files, browse the web, send emails).

This demo illustrates these concepts by building a simple "File Organizer Agent" in Python. The agent will leverage a local LLM (via Ollama) to categorize and move files based on their content (simulated by filename for simplicity).

---

## Prerequisites

Before running this demo, you need:

1.  **Python 3.8+**: Ensure Python is installed on your system.
2.  **Ollama**: A local LLM server.
    -   Download and install Ollama from [ollama.ai](https://ollama.ai/).
    -   Run Ollama in the background (it usually starts automatically after installation).
3.  **An LLM Model**: This demo uses `gemma:2b` as it's lightweight and efficient for local use.
    -   You need to pull this model using Ollama. Open your terminal or command prompt and run:
        ```bash
        ollama pull gemma:2b
        ```
    -   (You can try other models like `llama3` as well, but `gemma:2b` is a good starting point).

---

## Setup

1.  **Save the files**: Save the `agent.py` and `README.md` files into a new directory.
2.  **Navigate to the project directory** in your terminal or command prompt.
3.  **Install the required Python library**:
    ```bash
    pip install ollama
    ```

---

## How to Run

1.  **Ensure Ollama is running** in the background and you have pulled the `gemma:2b` model (see Prerequisites).
2.  **Execute the Python script** from your terminal:
    ```bash
    python agent.py
    ```

### What to Expect

The script will perform the following steps:

1.  **Initial Cleanup Check**: If a `test_files` directory exists and contains subdirectories (from a previous run), it will ask if you want to remove it to start with a clean slate for the demo. This ensures a consistent demonstration.
2.  **Directory Creation**: It will create a `test_files` directory if it doesn't already exist.
3.  **Dummy File Generation**: If the `test_files` directory is empty, the script will automatically create a few example files (e.g., `report_q1_2024.pdf`, `holiday_pic_beach.jpg`, `meeting_notes.txt`) to give the agent something to organize.
4.  **Observation**: The agent will list the files currently present in the `test_files` directory.
5.  **LLM Call (Thinking Phase)**: The agent will send the list of files to the `gemma:2b` model via Ollama, asking it to suggest categorizations and new paths. You'll see a message like "`--- Agent Thinking (Calling LLM) ---`".
6.  **Proposed Actions**: The agent will then display a clear list of proposed file moves (e.g., `report_q1_2024.pdf` -> `test_files/Reports/report_q1_2024.pdf`), including a reason for each suggestion.
7.  **User Confirmation (Human-in-the-Loop)**: You will be prompted to confirm whether you want to execute these actions. You need to type `yes` or `no`.
8.  **Action Execution**: If you confirm (`yes`), the agent will create the necessary category subdirectories (e.g., `test_files/Reports`, `test_files/Images`) and move the files accordingly.

### Example Interaction (Console Output)

```text
Starting File Organizer Agent for directory: 'test_files'
--------------------------------------------------
Checking 'test_files' for existing categories...
'test_files' contains subdirectories, suggesting a clean start for the demo.
Do you want to remove 'test_files' and its contents to start fresh? (y/n): y
Removing 'test_files'...
'test_files' removed.

Found 0 files in 'test_files':
No files found in 'test_files' to organize. Creating dummy files for demo...
 - Created 'report_q1_2024.pdf'
 - Created 'meeting_notes_2024-03-20.txt'
 - Created 'project_plan_v2.docx'
 - Created 'holiday_pic_beach.jpg'
 - Created 'recipe_pasta.md'
 - Created 'source_code_main.py'
 - Created 'archive.zip'
 - Created 'invoice_2023_12.pdf'

Found 8 files in 'test_files':
 - report_q1_2024.pdf
 - meeting_notes_2024-03-20.txt
 - project_plan_v2.docx
 - holiday_pic_beach.jpg
 - recipe_pasta.md
 - source_code_main.py
 - archive.zip
 - invoice_2023_12.pdf

--- Agent Thinking (Calling LLM) ---
LLM suggestions received and parsed.

--- Proposed File Organization Actions ---

1. File: 'report_q1_2024.pdf'
   Current Path: test_files/report_q1_2024.pdf
   Suggested Category: Reports
   New Path: test_files/Reports/report_q1_2024.pdf
   Reason: This is a financial report for Q1 2024.

2. File: 'meeting_notes_2024-03-20.txt'
   Current Path: test_files/meeting_notes_2024-03-20.txt
   Suggested Category: Notes
   New Path: test_files/Notes/meeting_notes_2024-03-20.txt
   Reason: This file contains meeting notes.

... (other suggestions) ...

Do you want to execute these actions? (yes/no): yes

--- Executing Actions ---
Created directory: test_files/Reports
Moved: 'report_q1_2024.pdf' to 'test_files/Reports'
Created directory: test_files/Notes
Moved: 'meeting_notes_2024-03-20.txt' to 'test_files/Notes'
...
Actions executed successfully!

--------------------------------------------------
Agent run finished.
```

After the script completes, inspect your `test_files` directory. You will find new subdirectories like `Reports`, `Notes`, `Images`, `Code`, etc., with the original files now organized within them.

---

## Why this is an "Agent"

This demo highlights the core components that elevate a stateless LLM to an agentic system:

1.  **Observation (Perception):** The `get_files_in_directory` function acts as the agent's "eyes," allowing it to perceive the state of its environment (the file system).
2.  **Planning/Reasoning (LLM Core):** The `get_llm_suggestions` function is where the LLM's "brain" comes into play. It processes the observed information (list of files) and generates a plan of action (categorization and moves). Since the LLM itself is stateless, the agent provides the complete context in each prompt, simulating short-term memory for the task.
3.  **Action (Tools):** The `create_directory_if_not_exists` and `move_file` functions are the agent's "hands." These are external tools that allow the agent to physically interact with and modify its environment.
4.  **Loop & Memory (Agent Orchestration):** The `run_file_organizer_agent` function orchestrates these steps (Observe -> Think -> Act) in a structured manner. This control flow creates the "loop." While explicit long-term memory isn't implemented here, the repeated observation and contextual prompting to the LLM serves as a basic form of operational memory.
5.  **Human-in-the-Loop:** The confirmation step (`confirm_and_execute_actions`) is a crucial design pattern for practical agents. It provides a safety net and allows human oversight and control before irreversible actions are taken.

This architecture demonstrates how combining a powerful but stateless LLM with external code that provides loops, tools, and a way to manage state can create intelligent, task-oriented agents capable of interacting with the real world.
