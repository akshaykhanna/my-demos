# Local Gemma 2 2B Chat Interface

This project contains a lightweight Python terminal interface to interact with Google's **Gemma 2 2B** model running locally on your machine using **Ollama**.

Because it uses standard libraries (`urllib` and `json`), you do not need to install any external python dependencies (`pip install`).

## Setup Instructions

### 1. Install Ollama
If you haven't already:
* Download and install Ollama from [ollama.com](https://ollama.com).
* Launch the Ollama application.

### 2. Download and Run Gemma 2 2B
Open your terminal (PowerShell, Command Prompt, or Git Bash) and pull/run the Gemma 2 2B model:
```powershell
ollama run gemma2:2b
```
*This will download the model (approx. 1.6 GB) and start an interactive session directly in your terminal. You can type `/exit` to close that session.*

### 3. Run the Python Chat Script
Ensure the Ollama application is running in the background. Then, run the script from this folder:
```powershell
python chat.py
```

## How it Works
* The script communicates with Ollama's local chat API (`http://localhost:11434/api/chat`).
* It preserves the conversation history dynamically to allow multi-turn interactions.
* It uses standard library calls so it works instantly on any standard Python 3 setup.
