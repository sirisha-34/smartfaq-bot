import speech_recognition as sr

def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I could not understand."
    except sr.RequestError:
        return "Sorry, speech API is unavailable."
