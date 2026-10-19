# Voice Assistant for PC

A Python voice assistant that uses speech recognition and text-to-speech to control your PC with voice commands.

## Features
- Open applications (Notepad, Calculator, Chrome, VS Code, etc.)
- Search Google and YouTube by voice
- Open websites ("go to github")
- System info: time, date, battery, CPU, memory, OS details
- Rule-based NLP intent parsing with fuzzy matching for app names

## Tech Stack
Python, SpeechRecognition, pyttsx3, psutil, NLP (regex intent parsing + difflib fuzzy matching)

## Setup
```bash
git clone https://github.com/<your-username>/voice-assistant.git
cd voice-assistant
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
python main.py
```

> If PyAudio fails to install on Windows, run: `pip install pipwin && pipwin install pyaudio`

## Example Commands
- "open notepad"
- "search for python tutorials"
- "play lofi music"
- "go to github"
- "what's the time"
- "battery status"
- "CPU usage"
- "exit"

## Notes
Speech recognition uses Google's free web API, so an internet connection is required.
