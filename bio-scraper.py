import speech_recognition as sr
import pyttsx3

def speak_text(text):
    """Convert text to speech."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen_to_speech():
    """Convert speech to text."""
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        print("Recognizing speech...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

    return None

if __name__ == "__main__":
    # Speak a welcome message
    speak_text("Hello, please say something!")

    # Listen to speech and convert it to text
    recognized_text = listen_to_speech()

    if recognized_text:
        # Respond back with the recognized text
        response = f"You said: {recognized_text}"
        speak_text(response)
