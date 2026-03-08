import speech_recognition as sr
import config
from speech import IS_SPEAKING
import time


r = sr.Recognizer()
mic = sr.Microphone()

# Base sensitivity
r.energy_threshold = 200
r.dynamic_energy_threshold = True



def listen():
    with mic as source:

        if config.LISTEN_MODE == "sensitive":
            r.adjust_for_ambient_noise(source, duration=1.2)
            r.energy_threshold = 250
        else:  # relax mode
            r.adjust_for_ambient_noise(source, duration=0.4)
            r.energy_threshold = 400

        r.pause_threshold = 0.7

        try:
            audio = r.listen(
                source,
                timeout=4,
                phrase_time_limit=8
            )
        except sr.WaitTimeoutError:
            return ""

    while IS_SPEAKING:
        time.sleep(0.1)


    try:
        query = r.recognize_google(audio, language="en-in")
        print("User:", query)
        return query.lower()
    except:
        return ""
