import ollama
import json
from tools import TOOL_MAP, AVAILABLE_TOOLS

# --- Configuration ---
MODEL_NAME = "llama3"  # Make sure you have 'ollama pull llama3' run

# --- Agent System Prompt ---
# This prompt instructs the LLM on its role, available tools, and how to respond.
# It's designed to make the LLM output a specific JSON format when it decides to use a tool.
SYSTEM_PROMPT = f"""
YOU ARE A HELPFUL AI ASSISTANT. You have access to the following tools: 

{json.dumps(AVAILABLE_TOOLS, indent=2)}

When asked to perform a task, you should first consider if any of the tools can help.
If you decide to use a tool, respond with a JSON object in the following format:

```json
{{
  "action": "call_tool",
  "tool_name": "TOOL_NAME",
  "tool_args": {{
    "ARG_NAME_1": "ARG_VALUE_1",
    "ARG_NAME_2": "ARG_VALUE_2"
  }}
}}
```

Do NOT add any other text before or after the JSON. Make sure the JSON is valid.

If you do not need to use a tool, or if the tool output provides a final answer, respond directly with your answer in plain text. Do not output JSON if you are not calling a tool.

If the user provides tool output, analyze it and provide a final answer.
"""

# --- Agent Logic ---

def run_agent(user_query: str) -> str:
    """
    Processes a user query by interacting with the LLM and potentially executing tools.
    
    Args:
        user_query (str): The natural language query from the user.

    Returns:
        str: The agent's final response after reasoning and tool execution.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]

    try:
        # First call to the LLM to decide on an action (tool call or direct answer)
        print("\nAgent: Thinking...")
        response = ollama.chat(model=MODEL_NAME, messages=messages, format="json") # Request JSON format from LLM
        llm_response_content = response['message']['content']

        # Attempt to parse the LLM's response as JSON to check for tool calls
        try:
            action = json.loads(llm_response_content)
            
            if action.get("action") == "call_tool" and action.get("tool_name"):
                tool_name = action["tool_name"]
                tool_args = action.get("tool_args", {})

                print(f"Agent: Decided to use tool: {tool_name}")

                if tool_name in TOOL_MAP:
                    print(f"Agent: Calling tool with arguments: {tool_args}")
                    # Execute the tool function dynamically
                    tool_output = TOOL_MAP[tool_name](**tool_args)
                    print(f"Tool Output: {tool_output}")

                    # After tool execution, send the tool's output back to the LLM
                    # as context for a final answer.
                    messages.append({"role": "assistant", "content": llm_response_content}) # The LLM's tool call decision
                    messages.append({"role": "user", "content": f"TOOL_OUTPUT: {tool_output}\n\nBased on this tool output, please provide a final summary or answer."})
                    
                    # Second call to LLM for final answer based on tool output
                    print("Agent: Getting final answer based on tool output...")
                    final_response = ollama.chat(model=MODEL_NAME, messages=messages)
                    return final_response['message']['content']
                else:
                    return f"Agent: Error - Unknown tool requested: {tool_name}"
            else:
                # If JSON was parsed but it's not a tool call action, treat as direct answer
                return llm_response_content
        except json.JSONDecodeError:
            # If the response is not valid JSON, it's a direct text answer
            return llm_response_content

    except Exception as e:
        return f"Agent encountered an error: {e}"

# --- Main Interaction Loop ---

if __name__ == "__main__":
    print("\n--- Basic LLM Agent Demo ---")
    print("Type your query, or 'exit' to quit.")

    while True:
        user_input = input("\nAgent: How can I help you today? (Type 'exit' to quit)\nYou: ")

        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        # Run the agent with the user's query
        agent_response = run_agent(user_input)
        print(f"\nAgent: {agent_response}")
