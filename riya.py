
from config import EXIT_WORDS
from wakeword import is_wake_word
from speech import speak
from listener import listen
from commands import handle_command

import sys
import time



def main():
    speak("Welcome back sir")

    while True:
        query = listen()

        if not query:
            continue

        # 🔴 GLOBAL EXIT (no wake word needed)
        if query.strip() == "exit" or query.strip() in EXIT_WORDS:
            speak("Shutting down. Goodbye.")

            while speech.IS_SPEAKING:
                time.sleep(0.1)
            
            sys.exit()

        # 🟢 WAKE WORD
        if is_wake_word(query):
            speak("Yes boss?")
            time.sleep(2)
            command = listen()

            if command:
                handle_command(command)

if __name__ == "__main__":
    main()