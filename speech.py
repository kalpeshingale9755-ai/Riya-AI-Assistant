# import subprocess

# def speak(text):
#     print(f"Riya: {text}")

#     command = f'''
#     Add-Type -AssemblyName System.Speech;
#     $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer;
#     $speak.SelectVoice("Microsoft Zira Desktop");
#     $speak.Rate = 0;
#     $speak.Speak("{text}");
#     '''

#     subprocess.run(
#         ["powershell", "-Command", command],
#         stdout=subprocess.DEVNULL,
#         stderr=subprocess.DEVNULL
#     )


import subprocess
import threading

IS_SPEAKING = False

def _speak_async(text):
    global IS_SPEAKING

    IS_SPEAKING = True

    command = f'''
    Add-Type -AssemblyName System.Speech;
    $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer;
    $speak.SelectVoice("Microsoft Zira Desktop");
    $speak.Rate = 0;
    $speak.Speak("{text}");
    '''

    subprocess.run(
        ["powershell", "-Command", command],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    IS_SPEAKING = False


def speak(text):
    print(f"Riya: {text}")
    t = threading.Thread(target=_speak_async, args=(text,), daemon=True)
    t.start()

 
