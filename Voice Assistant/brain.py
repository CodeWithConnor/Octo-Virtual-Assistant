import speech_recognition as sr
import datetime
from win10toast import ToastNotifier
import datetime
import os
import time
import pytz
import subprocess
import webbrowser
import sys
import pyttsx3
import config
from mailer import Mailer

def listen_for_commands():
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

    text = get_audio()

    # Text-to-speech
    def speak(text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    # Notes module
    def note(text):
        date = datetime.datetime.now()
        file_name = str(date).replace(":", "-") + "-note.txt"
        with open(file_name, "w") as f:
            f.write(text)

        subprocess.Popen(["notepad.exe", file_name])

    for phrase in config.NOTE_STRS:
        if phrase in text:
            speak("What would you like me to write down?")
            note_text = get_audio()
            note(note_text)
            speak("I've made a note of that.")

    # Help module
    for phrase in config.FEATURES_STRS:
        if phrase in text:
            webbrowser.open("https://github.com/ConnorHanks/Octo-Virtual-Assistant#features")
            ToastNotifier().show_toast("Octo: Virtual Assistant", "Here's a list of my current features.", threaded=True)

    # Google module
    for phrase in config.GOOGLE_SEARCH_STRS:
        if phrase in text:
            webbrowser.open("https://www.google.com/search?&q=" + text[18::])

    # Time module
    for phrase in config.TIME_STRS:
        if phrase in text:
            now = datetime.datetime.now()
            ToastNotifier().show_toast("Octo: Virtual Assistant", "It's " + now.strftime("%H:%M"), threaded=True)

    # Date module
    for phrase in config.DATE_STRS:
        if phrase in text:
            now = datetime.datetime.now()
            ToastNotifier().show_toast("Octo: Virtual Assistant", "It's " + now.strftime("%D"), threaded=True)
    
    # Open website module
    for phrase in config.OPEN_WEBSITE_STRS:
        if phrase in text:
            webbrowser.open("www." + text[13::], new=0)

    # Shutdown module
    for phrase in config.SHUTDOWN_STRS:
        if phrase in text:
            os.system("shutdown /s /t 1")

    # Restart module
    for phrase in config.RESTART_STRS:
        if phrase in text:
            os.system("shutdown /r")

    # Logout module
    for phrase in config.LOGOUT_STRS:
        if phrase in text:
            os.system("shutdown /l")

    # Sleep module
    for phrase in config.SLEEP_STRS:
        if phrase in text:
            os.system("shutdown /h")

    # Quit module
    for phrase in config.QUIT_STRS:
        if phrase in text:
            sys.exit(0)