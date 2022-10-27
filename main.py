from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import datetime
import pickle
import os.path
import sys
import time
import pyttsx3
import speech_recognition as sr
import pytz
import subprocess
import webbrowser
from win10toast import ToastNotifier
from playsound import playsound

# Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]


# Listens for microphone input using system's default device
def get_audio():
    r = sr.Recognizer()

    # Tries to interpret what the user said and converts it to text (heard)
    with sr.Microphone() as source:
        audio = r.listen(source)
        heard = ""
        try:
            heard = r.recognize_google(audio)
            print(heard)
        except Exception as e:
            print("Exception: " + str(e))
    return heard.lower()


# Used for responding to user
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def authenticate_google():
    # Uses the Google Calendar API to grab upcoming events (if any)
    # Uses the token.pickle to access the Google Calendar API
    creds = None # Set to none by default
    if os.path.exists("token.pickle"):
        with open("token.pickle", 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.pickle", 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def get_events(day, service):
    # Calls the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0])-12) + start_time.split(":")[1]
                start_time = start_time + "pm"

            speak(event["summary"] + " at " + start_time)


def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    # If the month mentioned is in the future, then set the year to the next year
    if month < today.month and month != -1:
        year = year+1

    # If there is no specific month mentioned, but we have the day
    if month == -1 and day != -1:
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    # If there is only a day of the week mentioned
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1: 
        return datetime.date(month=month, day=day, year=year)

# Uses notepad.exe to create and store notes
def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)
    subprocess.Popen(["notepad.exe", file_name])

# Here we define the wake word and the commands that the assistant can respond to
WAKE = "Octo"
SERVICE = authenticate_google()
print("Started listening...")

while True:
    text = get_audio()

    if text.count(WAKE) > 0:
        text = get_audio()

        # Commands
        CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]
        for phrase in CALENDAR_STRS:
            if phrase in text:
                date = get_date(text)
                if date:
                    get_events(date, SERVICE)
                else:
                    speak("I don't understand")

        NOTE_STRS = ["make a note", "write this down", "remember this"]
        for phrase in NOTE_STRS:
            if phrase in text:
                speak("What would you like me to write down?")
                note_text = get_audio()
                note(note_text)
                speak("I've made a note of that.")

        FEATURES_STRS = ["what can you do", "what are your features", "what features do you have"]
        for phrase in FEATURES_STRS:
            if phrase in text:
                webbrowser.open("https://github.com/CodeWithConnor/Octo-Virtual-Assistant#features")
                ToastNotifier().show_toast("Octo: Virtual Assistant", "Here's a list of my current features.", threaded=True)

        GOOGLE_STRS = ["search google"]
        for phrase in GOOGLE_STRS:
            if phrase in text:
                speak("what for?")
                text = get_audio()
                webbrowser.open("https://www.google.com/search?&q=" + text)

        TIME_STRS = ["what's the time", "what time is it", "tell me the time"]
        for phrase in TIME_STRS:
            if phrase in text:
                now = datetime.datetime.now()
                ToastNotifier().show_toast("Octo: Virtual Assistant", "It's " + now.strftime("%H:%M"), threaded=True)

        DATE_STRS = ["what's the date", "what date is it", "tell me the date", "what's today's date"]
        for phrase in DATE_STRS:
            if phrase in text:
                now = datetime.datetime.now()
                ToastNotifier().show_toast("Octo: Virtual Assistant", "It's " + now.strftime("%D"), threaded=True)

        QUIT_STRS = ["quit", "exit", "close"]
        for phrase in QUIT_STRS:
            if phrase in text:
                sys.exit(0)