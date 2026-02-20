from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import librosa
import numpy as np
import tempfile
import shutil
import time

from fingerprint import generate_fingerprint
from database import save_fingerprints, match_fingerprints, get_all_songs
from microphone import record_audio

app = FastAPI(title="My song recognition")

@app.get("/songs")
def list_songs():
    songs = get_all_songs()
    return {"songs": songs}

@app.post("/listen")
def listen_microphone():
    print("Starting continuous listening...")

    buffer = np.array([])
    sample_rate = 44100

    max_seconds = 20
    chunk_duration = 1
    window_size = 5
    threshold = 200

    start_time = time.time()

    while True:

        # nagrywamy 1 sekundę
        y, sr = record_audio(duration=chunk_duration)
        buffer = np.concatenate((buffer, y))

        # jeśli mamy co najmniej 5 sekund audio
        if len(buffer) >= sample_rate * window_size:

            print("Analyzing window...")

            fingerprints = generate_fingerprint(buffer, sr)
            song, match_count = match_fingerprints(fingerprints)

            if song and match_count > threshold:
                print("Song detected:", song)
                return {
                    "detected_song": song,
                    "match_count": match_count,
                    "confidence": round(match_count / len(fingerprints), 3)
                }

            # przesuwamy okno o 1 sekundę
            buffer = buffer[sample_rate:]

        # timeout
        if time.time() - start_time > max_seconds:
            print("Timeout reached.")
            return {
                "detected_song": None,
                "match_count": 0,
                "confidence": 0
            }

@app.post("/index")
async def index_song(file: UploadFile = File(...), name: str = "Unknown Song"):

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        shutil.copyfileobj(file.file, temp)
        temp_path = temp.name

    y, sr = librosa.load(temp_path, mono=True)
    fingerprints = generate_fingerprint(y, sr)
    save_fingerprints(name, fingerprints)

    return {"status": "indexed", "fingerprints": len(fingerprints)}


@app.post("/identify")
async def identify_song(file: UploadFile = File(...)):

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        shutil.copyfileobj(file.file, temp)
        temp_path = temp.name

    y, sr = librosa.load(temp_path, mono=True)
    fingerprints = generate_fingerprint(y, sr)
    song = match_fingerprints(fingerprints)

    return {"detected_song": song}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>My song recognition</title>
        </head>
        <body style="font-family: Arial; text-align:center; margin-top:100px;">
            <h1> Shazam Clone</h1>
            <button onclick="listen()">Start Listening</button>
            <h2 id="status"></h2>

            <script>
                async function listen() {
                    document.getElementById("status").innerText = "Listening...";

                    const response = await fetch("/listen", {
                        method: "POST"
                    });

                    const data = await response.json();

                    if (data.detected_song) {
                        document.getElementById("status").innerText =
                            "Detected: " + data.detected_song +
                            "(confidence: " + data.confidence + ")";
                    } else {
                        document.getElementById("status").innerText =
                            "No song detected.";
                    }
                }
            </script>
        </body>
    </html>
    """