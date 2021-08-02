from __future__ import print_function
import pyttsx3
import speech_recognition as sr
from playsound import playsound
from config import *
from brain import listen_for_commands

print("Virtual Assistant loaded.")

listening_for_commands = False

# Listen using system's default microphone
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""
        # Convert user's microphone input to text
        try:
            said = r.recognize_google(audio)
            print(said)
        # If unintelligable, throw an exception
        except Exception as e:
            print("Exception: " + str(e))
    return said.lower()

# Always listen for wake word
while True:
    print("I'm listening...")
    text = get_audio()
    # If wake word detected, start listening for commands
    if text.lower() in wake_word:
        playsound(listening, block=False)
        listen_for_commands()