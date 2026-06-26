import json
import urllib.request
import urllib.error
import sys

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma2:2b"

def send_chat_message(messages):
    """Sends the chat history to the local Ollama instance and returns the model response."""
    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False
    }
    
    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            return res_json.get("message", {}).get("content", "")
    except urllib.error.URLError as e:
        print(f"\n[Error] Could not connect to Ollama. Is it running? Details: {e}")
        print("Please make sure Ollama is running (`ollama serve` or open the Ollama app) and that the model is loaded.")
        sys.exit(1)

def main():
    print("=" * 60)
    print(f" Gemma 2 2B - Local Chat Session via Ollama ".center(60, "="))
    print(f"Model: {MODEL_NAME}")
    print("Type 'exit' or 'quit' to end the session.")
    print("=" * 60)
    
    messages = []
    
    # Optional system prompt to instruct the model to behave like a helpful assistant
    messages.append({
        "role": "system",
        "content": "You are a helpful, concise, and friendly AI assistant running locally on the user's computer."
    })
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("\nGoodbye!")
                break
                
            messages.append({"role": "user", "content": user_input})
            
            print("Gemma: thinking...", end="\r")
            response_content = send_chat_message(messages)
            
            # Clear the "thinking..." line and print the actual response
            print(" " * 20, end="\r")
            print(f"Gemma: {response_content}")
            
            # Keep history context
            messages.append({"role": "assistant", "content": response_content})
            
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break

if __name__ == "__main__":
    main()
