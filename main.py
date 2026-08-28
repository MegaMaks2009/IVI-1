import json
import os
import psutil
import win32gui
import win32con
import win32process
import subprocess
import sherpa_onnx
import winsound
import sounddevice as sd
from rapidfuzz import process, fuzz


logo = """ █████ █████   █████ █████
▒▒███ ▒▒███   ▒▒███ ▒▒███
 ▒███  ▒███    ▒███  ▒███
 ▒███  ▒███    ▒███  ▒███
 ▒███  ▒▒███   ███   ▒███
 ▒███   ▒▒▒█████▒    ▒███
 █████    ▒▒███      █████
▒▒▒▒▒      ▒▒▒      ▒▒▒▒▒

"""


def print_config(text=""):
    os.system("cls")
    print(logo)
    print(f"You say: {text}", flush=True)


def open_program(path):
    exe = os.path.basename(path).lower()

    for app in psutil.process_iter(["pid", "name"]):
        name = app.info["name"]

        if not name or name.lower() != exe:
            continue

        windows = []

        def find_window(hwnd, _):
            pid = win32process.GetWindowThreadProcessId(hwnd)[1]

            if win32gui.IsWindowVisible(hwnd) and pid == app.info["pid"]:
                windows.append(hwnd)

        win32gui.EnumWindows(find_window, None)

        if windows:
            window = windows[0]

            win32gui.ShowWindow(window, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(window)

            return

    subprocess.Popen([path])


def find_command(words):
    for i in range(len(words) - 1, -1, -1):
        match = process.extractOne(
            words[i],
            ["open", "close", "exit"],
            scorer=fuzz.ratio,
            score_cutoff=75
        )

        if match:
            return match[0], words[i:]

    return None, words


def reset_recognition():
    print_config()
    return recognizer.create_stream(), ""


programs = json.load(
    open("data/programs.json", encoding="utf-8")
)


recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
    tokens="stt model/tokens.txt",
    encoder="stt model/encoder.onnx",
    decoder="stt model/decoder.onnx",
    joiner="stt model/joiner.onnx",
    num_threads=2,
    sample_rate=16000,
    feature_dim=80,
    decoding_method="greedy_search",
    provider="cpu"
)


stream = recognizer.create_stream()
last = ""


os.system("title IVI Config")

print_config()

winsound.PlaySound(
    "data/sounds/launch.wav",
    winsound.SND_FILENAME | winsound.SND_ASYNC
)


with sd.InputStream(
    channels=1,
    dtype="float32",
    samplerate=16000,
    blocksize=320,
    latency="low"
) as mic:

    while True:
        audio, _ = mic.read(320)

        stream.accept_waveform(
            16000,
            audio.reshape(-1)
        )

        while recognizer.is_ready(stream):
            recognizer.decode_stream(stream)

        text = recognizer.get_result(stream).lower().strip()

        if text != last:
            last = text
            words = text.split()

            if words:
                command, words = find_command(words)

                print_config(text)

                if command == "exit":
                    break

                if command in ["open", "close"] and len(words) > 1:
                    name = " ".join(words[1:])

                    match = process.extractOne(
                        name,
                        programs.keys(),
                        scorer=fuzz.ratio,
                        score_cutoff=65
                    )

                    if match:
                        path = programs[match[0]]

                        if command == "open":
                            open_program(path)

                        else:
                            exe = os.path.basename(path).lower()

                            for app in psutil.process_iter(["name"]):
                                app_name = app.info["name"]

                                if app_name and app_name.lower() == exe:
                                    app.kill()

                        stream, last = reset_recognition()