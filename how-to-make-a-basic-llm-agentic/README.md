# Basic LLM Agent Demo

This project demonstrates a simple LLM (Large Language Model) agent capable of using a basic tool to interact with the file system. An LLM agent is more than just a chatbot; it's a 'helper' that can understand your request, decide if it needs to perform an action (like running code or using a tool), execute that action, and then use the results to formulate a response.

## What this Demo Does

This demo features a Python script that acts as a basic LLM agent. It uses an open-source model (like Llama 3 via Ollama) and is equipped with a single tool: `write_to_file`. When you give the agent a prompt that requires writing to a file, it will:

1.  **Understand your intent**: Analyze the request.
2.  **Decide to use a tool**: Recognize that the `write_to_file` tool is needed.
3.  **Format the tool call**: Generate a structured (JSON) command for the tool.
4.  **Execute the tool**: Call the actual Python function `write_to_file` with the specified arguments.
5.  **Provide a response**: Give you feedback on the tool's execution.

## Prerequisites

Before running this demo, you need to have the following installed and set up:

1.  **Python 3.9+**: [Download Python](https://www.python.org/downloads/)
2.  **Ollama**: A platform for running open-source LLMs locally.
    *   Download and install Ollama from [ollama.com](https://ollama.com/).
3.  **Llama 3 Model**: Once Ollama is installed, pull the Llama 3 model by running this command in your terminal:
    ```bash
    ollama pull llama3
    ```

## Setup and Installation

1.  **Clone this repository** (or create the files manually):
    ```bash
    # Assuming you have git
    git clone <repository_url>
    cd <repository_directory>
    
    # If you're creating files manually, just navigate to your project directory
    ```

2.  **Install Python dependencies**: Navigate to the project directory in your terminal and install the `ollama` Python client:
    ```bash
    pip install ollama
    ```

## How to Run

1.  Ensure your Ollama server is running in the background (it usually starts automatically after installation).
2.  Run the `main.py` script from your terminal:
    ```bash
    python main.py
    ```
3.  The script will prompt you to enter a query. Try prompts like:
    *   `Write a note to a file called 'meeting_summary.txt' with the content 'The meeting covered Q3 results and planning for Q4.'`
    *   `Could you please create a new file named 'todo.txt' and put 'Buy groceries, Walk the dog, Finish report' inside it?`
    *   `What is the capital of France?` (This will show the agent responding directly without a tool).

## Expected Output

When you run the script and provide a tool-requiring prompt, you will see output similar to this:

```
Agent: How can I help you today? (Type 'exit' to quit)
You: Write a note to a file called 'meeting_summary.txt' with the content 'The meeting covered Q3 results and planning for Q4.'

Agent: Decided to use tool: write_to_file
Agent: Calling tool with arguments: {'filename': 'meeting_summary.txt', 'content': 'The meeting covered Q3 results and planning for Q4.'}
Tool Output: Successfully wrote content to meeting_summary.txt
Agent: I have successfully written the content to 'meeting_summary.txt'.

Agent: How can I help you today? (Type 'exit' to quit)
You: What is the capital of France?

Agent: The capital of France is Paris.

Agent: How can I help you today? (Type 'exit' to quit)
You: exit
Goodbye!
```

You will also find the `meeting_summary.txt` (or whatever filename you specified) file created in the same directory as `main.py` with the content you provided.