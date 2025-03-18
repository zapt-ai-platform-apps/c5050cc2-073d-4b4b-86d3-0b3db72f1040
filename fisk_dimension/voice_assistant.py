import pyttsx3
import speech_recognition as sr

# Initialize text-to-speech engine.
engine = pyttsx3.init()
voices = engine.getProperty('voices')
# Set the voice (change index as desired).
engine.setProperty('voice', voices[1].id)

def speak(text: str):
    """Speak out text using your personal AI voice assistant."""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen_command() -> str:
    """Listen for a voice command and return the recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your command...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio, language="en-US")
            print(f"You said: {command}")
            return command
        except Exception as e:
            print("Listening error:", str(e))
            return ""