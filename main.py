"""
Voice Assistant for PC
Python | SpeechRecognition | pyttsx3 (TTS) | Rule-based NLP intent parsing
"""

import difflib
import datetime
import platform
import re
import subprocess
import sys
import urllib.parse
import webbrowser

import psutil
import pyttsx3
import speech_recognition as sr

OS = platform.system()  # "Windows", "Darwin", "Linux"

# ---------- Text-to-Speech ----------
engine = pyttsx3.init()
engine.setProperty("rate", 175)


def speak(text: str) -> None:
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()


# ---------- Speech Recognition ----------
recognizer = sr.Recognizer()


def listen() -> str:
    """Capture microphone input and return lowercase text ('' on failure)."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return ""
    try:
        text = recognizer.recognize_google(audio).lower()
        print(f"You: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Speech service is unavailable. Check your internet connection.")
        return ""


# ---------- Application launcher ----------
APPS = {
    "Windows": {
        "notepad": "notepad", "calculator": "calc", "paint": "mspaint",
        "command prompt": "cmd", "file explorer": "explorer",
        "task manager": "taskmgr", "chrome": "chrome", "edge": "msedge",
        "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
        "vs code": "code", "settings": "ms-settings:",
    },
    "Darwin": {
        "notepad": "TextEdit", "calculator": "Calculator", "chrome": "Google Chrome",
        "safari": "Safari", "terminal": "Terminal", "vs code": "Visual Studio Code",
        "settings": "System Settings",
    },
    "Linux": {
        "notepad": "gedit", "calculator": "gnome-calculator", "terminal": "gnome-terminal",
        "chrome": "google-chrome", "firefox": "firefox", "vs code": "code",
        "file explorer": "nautilus",
    },
}


def open_app(name: str) -> None:
    apps = APPS.get(OS, {})
    match = difflib.get_close_matches(name, apps.keys(), n=1, cutoff=0.6)
    if not match:
        speak(f"I don't know how to open {name}.")
        return
    target = apps[match[0]]
    try:
        if OS == "Windows":
            subprocess.Popen(f'start "" "{target}"', shell=True)
        elif OS == "Darwin":
            subprocess.Popen(["open", "-a", target])
        else:
            subprocess.Popen([target])
        speak(f"Opening {match[0]}.")
    except Exception as exc:
        speak(f"Could not open {match[0]}.")
        print(exc)


# ---------- Web actions ----------
def search_web(query: str) -> None:
    speak(f"Searching the web for {query}.")
    webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(query))


def play_youtube(query: str) -> None:
    speak(f"Searching YouTube for {query}.")
    webbrowser.open(
        "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
    )


def open_website(site: str) -> None:
    site = site.replace(" dot ", ".").replace(" ", "")
    if "." not in site:
        site += ".com"
    speak(f"Opening {site}.")
    webbrowser.open("https://" + site)


# ---------- System information ----------
def tell_time() -> None:
    speak("The time is " + datetime.datetime.now().strftime("%I:%M %p"))


def tell_date() -> None:
    speak("Today is " + datetime.datetime.now().strftime("%A, %B %d, %Y"))


def battery_status() -> None:
    battery = psutil.sensors_battery()
    if battery is None:
        speak("No battery detected on this device.")
        return
    state = "charging" if battery.power_plugged else "not charging"
    speak(f"Battery is at {int(battery.percent)} percent and {state}.")


def cpu_usage() -> None:
    speak(f"CPU usage is {psutil.cpu_percent(interval=1)} percent.")


def memory_usage() -> None:
    mem = psutil.virtual_memory()
    speak(f"Memory usage is {mem.percent} percent. "
          f"{round(mem.available / 1e9, 1)} gigabytes are free.")


def system_info() -> None:
    speak(f"You are running {platform.system()} {platform.release()} "
          f"on a {platform.machine()} processor.")


# ---------- NLP: rule-based intent parsing ----------
# Each entry: (intent, regex). Group 1 captures the entity, if any.
INTENT_PATTERNS = [
    ("open_website", r"(?:go to|open website|visit)\s+(.+)"),
    ("play_youtube", r"(?:play|youtube)\s+(.+)"),
    ("search_web", r"(?:search for|search|google|look up)\s+(.+)"),
    ("open_app", r"(?:open|launch|start)\s+(.+)"),
    ("time", r"\b(?:time)\b"),
    ("date", r"\b(?:date|day today|today's date)\b"),
    ("battery", r"\bbattery\b"),
    ("cpu", r"\bcpu\b|\bprocessor usage\b"),
    ("memory", r"\bmemory\b|\bram\b"),
    ("system_info", r"system (?:info|information)|about (?:my )?(?:pc|computer)"),
    ("help", r"\bhelp\b|what can you do"),
    ("exit", r"\b(?:exit|quit|stop|goodbye|bye)\b"),
]


def parse_intent(text: str):
    for intent, pattern in INTENT_PATTERNS:
        m = re.search(pattern, text)
        if m:
            entity = m.group(1).strip() if m.groups() else None
            return intent, entity
    return None, None


def handle(text: str) -> bool:
    """Run the command. Returns False when the assistant should exit."""
    intent, entity = parse_intent(text)

    actions = {
        "open_website": lambda: open_website(entity),
        "play_youtube": lambda: play_youtube(entity),
        "search_web": lambda: search_web(entity),
        "open_app": lambda: open_app(entity),
        "time": tell_time,
        "date": tell_date,
        "battery": battery_status,
        "cpu": cpu_usage,
        "memory": memory_usage,
        "system_info": system_info,
        "help": lambda: speak(
            "I can open apps, search the web, play YouTube, "
            "and tell you the time, date, battery, CPU and memory usage."
        ),
    }

    if intent == "exit":
        speak("Goodbye!")
        return False
    if intent in actions:
        actions[intent]()
    else:
        speak("Sorry, I didn't understand that. Say help to hear what I can do.")
    return True


def main() -> None:
    speak("Voice assistant started. How can I help you?")
    running = True
    while running:
        command = listen()
        if command:
            running = handle(command)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)