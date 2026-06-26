# Local LLM Voice Tasker (Windows)

A modular local AI agent that uses Google's **Gemma 2 2B** via **Ollama** to launch apps or search for missing app downloads on Windows using voice or text commands.

Unlike hardcoded solutions, this agent **dynamically searches your Start Menu shortcuts** to launch any software installed on your machine.

---

## 🛠️ Project Structure

* **`agent.py`**: The orchestrator that manages the ReAct loop, system prompts, Ollama querying, and parses tool execution.
* **`tools.py`**: Defines filesystem and system tools (`open_application` and `search_download_page`). It recursively searches Start Menu directories (`.lnk` files) on Windows.
* **`voice.py`**: Captures microphone input and converts it to text using Google Speech Recognition API.

---

## ⚙️ Installation & Setup

### 1. Install Ollama and Gemma 2 2B
Make sure you have Ollama installed and the Gemma 2 2B model downloaded:
```powershell
# In PowerShell or Command Prompt
ollama run gemma2:2b
```

### 2. Install Python Dependencies
Install the required Speech Recognition and audio capture libraries:
```powershell
pip install SpeechRecognition pyaudio
```
*(If you encounter issues installing `pyaudio` on Windows, you can install the pre-compiled wheel using `pip install pipwin` then `pipwin install pyaudio`.)*

---

## 🚀 Running the Agent

Start the agent:
```powershell
python agent.py
```

Upon launching, the script will prompt you:
```
============================================================
                  Local LLM Tasker Agent                    
============================================================
Choose your input mode:
  [1] Text Chat (type commands directly)
  [2] Voice Command (speak into your microphone)
============================================================
```
Type **`1`** or **`2`** to select your input mode.

---

## 💬 Sample Prompts

Here are some prompts you can type or speak to test the agent:

* **Open an installed application:**
  * *"Open Google Chrome please."*
  * *"Start Spotify."*
  * *"Launch Notepad."*
  
* **Handle a missing application (Fallback to download):**
  * *"Launch Zoom. If it's not installed, help me download it."*
  * *"Open Steam, or search for its download page if I don't have it."*
