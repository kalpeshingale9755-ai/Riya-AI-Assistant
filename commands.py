import os
import sys
import time
import datetime
import subprocess
import webbrowser

from speech import speak
from config import EXIT_WORDS
import config


# ===============================
# 🔍 AUTO-DETECT APPS (IMPROVED)
# ===============================
START_MENU_PATHS = [
    os.path.join(os.environ["PROGRAMDATA"], "Microsoft", "Windows", "Start Menu", "Programs"),
    os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
]

AUTO_APPS = {}        # token -> shortcut path
DISPLAY_NAMES = {}   # token -> full app name


def build_app_index():
    AUTO_APPS.clear()
    DISPLAY_NAMES.clear()

    for base in START_MENU_PATHS:
        for root, _, files in os.walk(base):
            for file in files:
                # if file.endswith(".lnk"):
                #     # ignore unwanted shortcuts
                #     if any(bad in full_name for bad in ["uninstall", "updater", "helper"]):
                #         continue
                #         full_name = file.replace(".lnk", "").lower()
                #         path = os.path.join(root, file)

                #         # full name mapping
                #         AUTO_APPS[full_name] = path
                #         DISPLAY_NAMES[full_name] = full_name

                #         # token mapping (for vscode, obs, chrome etc.)
                #         for token in full_name.split():
                #             if len(token) > 2:
                #                 AUTO_APPS[token] = path
                #                 DISPLAY_NAMES[token] = full_name

                if file.endswith(".lnk"):
                    full_name = file.replace(".lnk", "").lower()
                    path = os.path.join(root, file)

                    # ignore unwanted shortcuts
                    if any(bad in full_name for bad in ["uninstall", "updater", "helper"]):
                        continue

                    # full name mapping
                    AUTO_APPS[full_name] = path
                    DISPLAY_NAMES[full_name] = full_name

                    # token mapping
                    for token in full_name.split():
                        if len(token) > 2:
                            AUTO_APPS[token] = path
                            DISPLAY_NAMES[token] = full_name



build_app_index()


# ===============================
# 🧠 UTILITIES
# ===============================
def close_process(exe):
    subprocess.run(
        ["taskkill", "/f", "/im", exe, "/t"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# ===============================
# 📂 MANUAL OPEN COMMANDS
# ===============================
OPEN_COMMANDS = {
    "notepad": lambda: subprocess.Popen("notepad", shell=True),
    "calculator": lambda: subprocess.Popen("calc", shell=True),
    "paint": lambda: subprocess.Popen("mspaint", shell=True),
    "cmd": lambda: subprocess.Popen("cmd", shell=True),
    "powershell": lambda: subprocess.Popen("powershell", shell=True),
    "whatsapp" : lambda: subprocess.Popen(
    'explorer shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App',
    shell=True),
    # "vscode": lambda: subprocess.Popen("Code.exe", shell=True),
    # "spotify": lambda: subprocess.Popen("shell:AppsFolder\\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify", shell=True),
    "vscode": lambda: subprocess.Popen(
    r"C:\Users\YOUR_USERNAME\AppData\Local\Programs\Microsoft VS Code\Code.exe"),
}

# ===============================
# ❌ MANUAL CLOSE COMMANDS
# ===============================
CLOSE_COMMANDS = {
    "notepad": "notepad.exe",
    "chrome": "chrome.exe",
    "spotify": "spotify.exe",
    "whatsapp": "WhatsApp.exe",
}

# ===============================
# 🧠 EXECUTABLE OVERRIDES (IMPORTANT)
# ===============================
EXE_MAP = {
    "google chrome": "chrome.exe",
    "chrome": "chrome.exe",
    "visual studio code": "Code.exe",
    "vscode": "Code.exe",
    "code": "Code.exe",
    "obs": "obs64.exe",
    "obs studio": "obs64.exe",
    "spotify": "spotify.exe",
    "whatsapp" : "WhatsApp.exe",
    "photoshop": "Photoshop.exe",
    "adobe photoshop": "Photoshop.exe",
    "vlc": "vlc.exe",
    "vlc media player": "vlc.exe",
    "powerpoint": "POWERPNT.EXE",
    "excel": "EXCEL.EXE",
    "access": "MSACCESS.EXE",
    "opera": "opera.exe",
    "control panel": "control.exe",
    "git bash": "mintty.exe",
    "adobe reader": "AcroRd32.exe",

}

def resolve_process_name(app):
    # direct map first
    if app in EXE_MAP:
        return EXE_MAP[app]

    # already an exe
    if app.endswith(".exe"):
        return app

    # fallback
    return app + ".exe"




def normalize_command(command):
    command = command.lower()

    # remove filler words
    fillers = [
        "please", "can you", "could you", "would you",
        "hey", "riya", "for me", "kindly", "just"
    ]

    for word in fillers:
        command = command.replace(word, "")

    # normalize verbs
    command = command.replace("launch", "open")
    command = command.replace("start", "open")
    command = command.replace("run", "open")

    command = command.replace("terminate", "close")
    command = command.replace("kill", "close")
    command = command.replace("stop", "close")

    # normalize app words
    command = command.replace("application", "")
    command = command.replace("app", "")
    command = command.replace("software", "")

    # remove extra spaces
    command = " ".join(command.split())
    return command


def apply_aliases(command):
    words = command.split()
    new_words = []

    for word in words:
        replaced = False

        for alias, real in ALIASES.items():
            if word == alias:
                new_words.append(real)
                replaced = True
                break

        if not replaced:
            new_words.append(word)

    return " ".join(new_words)




ALIASES = {
    # browsers
    "browser": "chrome.exe",
    "web": "chrome.exe",

    # music
    "music": "spotify",
    "song": "spotify",
    "songs": "spotify",

    # coding
    "editor": "vscode",
    "code editor": "vscode",
    "code": "vscode",
    "vs code": "vs code",

    # terminal
    "terminal": "cmd",
    "command prompt": "cmd",
    "shell": "cmd",
}





# ===============================
# 🎯 MAIN HANDLER
# ===============================
def handle_command(command):
    command = normalize_command(command)
    command = apply_aliases(command)

    # ===============================
    # 🎧 LISTENING MODE CONTROL
    # ===============================
    if "sensitive mode" in command:
        config.LISTEN_MODE = "sensitive"
        speak("Sensitive mode activated")
        return

    if "relax mode" in command or "silent mode" in command:
        config.LISTEN_MODE = "relax"
        speak("Relax mode activated")
        return

    # ===============================
    # ❌ CLOSE APP (FIXED VERSION)
    # ===============================
    if command.startswith("close "):
        app = command.replace("close", "").strip()

        # print("DEBUG: trying to close:", app)

        # manual close first
        if app in CLOSE_COMMANDS:
            exe = CLOSE_COMMANDS[app]
            close_process(exe)
            speak(f"Closing {app}")
            return

        # try EXE_MAP
        if app in EXE_MAP:
            exe = EXE_MAP[app]
            close_process(exe)
            speak(f"Closing {app}")
            return

        # try AUTO_APPS display name
        for key in AUTO_APPS:
            if app in key or key in app:
                display = DISPLAY_NAMES[key]

                # First try EXE_MAP using user app name
                if app in EXE_MAP:
                    exe = EXE_MAP[app]
                # Then try EXE_MAP using display name
                elif display in EXE_MAP:
                    exe = EXE_MAP[display]
                else:
                    exe = resolve_process_name(display)

                close_process(exe)
                speak(f"Closing {display}")
                return

                
        speak("I couldn't find that app to close")
        return


    # ===============================
    # 📂 OPEN APP (SAFE FIX)
    # ===============================
    if command.startswith("open "):
        app = command.replace("open", "").strip()

        # print("DEBUG: trying to open:", app)

        # manual apps
        if app in OPEN_COMMANDS:
            speak(f"Opening {app}")
            OPEN_COMMANDS[app]()
            return

       

        # try AUTO_APPS with smart matching
        best_match = None

        for key in AUTO_APPS:
            if app in key or key in app:
                best_match = key
                break

        if best_match:
            speak(f"Opening {DISPLAY_NAMES[best_match]}")
            try:
                os.startfile(AUTO_APPS[best_match])
            except Exception:
                speak("Failed to open app")
            return

        # fallback direct start (FIXED)
        exe = resolve_process_name(app)

        try:
            speak(f"Opening {app}")
            subprocess.Popen(exe, shell=True)
            return
        except:
            pass

    # ===============================
    # 🔍 SEARCH ON CHROME
    # ===============================
    if "search" in command and "chrome" in command:
        query = command.replace("search", "").replace("on chrome", "").replace("chrome", "").strip()
        if query:
            speak(f"Searching on chrome for {query}")
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        else:
            speak("What should I search for?")
        return

    # ===============================
    # 🖥️ SYSTEM COMMANDS
    # ===============================
    SYSTEM_COMMANDS = {
        "open settings": lambda: subprocess.Popen("start ms-settings:", shell=True),
        "lock screen": lambda: subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True),
        "shutdown system": lambda: subprocess.Popen("shutdown /s /t 5", shell=True),
        "restart system": lambda: subprocess.Popen("shutdown /r /t 5", shell=True),
    }

    for key, action in SYSTEM_COMMANDS.items():
        if key in command:
            speak(key.replace("open", "opening"))
            action()
            return

    # ===============================
    # 🌐 BROWSER COMMANDS
    # ===============================
    if "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
        return

    if "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
        return

    # ===============================
    # ℹ️ INFO
    # ===============================
    if "time" in command:
        speak(datetime.datetime.now().strftime("The time is %I:%M %p"))
        return

    if "date" in command:
        speak(datetime.datetime.now().strftime("Today is %A %d %B %Y"))
        return

    speak("Sorry, I don't know this command yet")
