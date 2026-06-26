import speech_recognition as sr

def listen_for_command() -> str:
    """Captures microphone input and transcribes it to text using Google Speech Recognition."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n" + "=" * 40)
        print(" Listening for your command... Speak now! ".center(40, "="))
        print("=" * 40)
        
        # Calibration for background noise
        recognizer.adjust_for_ambient_noise(source, duration=1)
        # Give the user more time to pause between words (default is 0.8s)
        recognizer.pause_threshold = 3.0
        # Listen with a timeout and phrase limit of 120 seconds (2 minutes)
        audio = recognizer.listen(source, timeout=120, phrase_time_limit=120)
        
    try:
        print("Transcribing...")
        command = recognizer.recognize_google(audio)
        print(f"Voice Detected: \"{command}\"")
        return command
    except sr.UnknownValueError:
        print("Speech Recognition could not understand the audio.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request speech recognition service; {e}")
        return ""
