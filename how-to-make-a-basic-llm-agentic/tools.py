import os

# --- Tool Definitions ---

# This file contains the actual Python functions that our LLM Agent can 'call'.
# Each function represents a capability or an action the agent can perform.

# For this simple demo, we have one tool: 'write_to_file'.

def write_to_file(filename: str, content: str) -> str:
    """
    Writes the given content to a specified file. If the file exists, it will be overwritten.

    Args:
        filename (str): The name of the file to write to (e.g., 'notes.txt').
                        The file will be created in the current working directory.
        content (str): The string content to write into the file.

    Returns:
        str: A message indicating the success or failure of the write operation.
    """
    try:
        # Ensure the filename is safe for the current directory
        # For a real-world application, consider stricter path sanitization or
        # defining a specific directory for agent-created files.
        file_path = os.path.join(os.getcwd(), filename)
        
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote content to {filename}"
    except IOError as e:
        return f"Error writing to file {filename}: {e}"


# This dictionary maps tool names (as recognized by the LLM) to their actual Python functions.
# It's crucial for the agent to be able to execute the tool once it decides to call it.
TOOL_MAP = {
    "write_to_file": write_to_file,
}

# This list describes the available tools to the LLM. It's used in the system prompt
# to inform the LLM about what tools it has access to, their purpose, and their parameters.
# The 'parameters' schema follows JSON Schema conventions.
AVAILABLE_TOOLS = [
    {
        "name": "write_to_file",
        "description": "Writes the specified content to a file. If the file exists, it will be overwritten.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the file to write to (e.g., 'notes.txt')."
                },
                "content": {
                    "type": "string",
                    "description": "The content to write into the file."
                }
            },
            "required": ["filename", "content"]
        }
    }
]
