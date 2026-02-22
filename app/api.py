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
    threshold = 0.02

    start_time = time.time()

    while True:

        # nagrywamy 1 sekundę
        y, sr = record_audio(duration=chunk_duration)
        buffer = np.concatenate((buffer, y))

        # jeśli mamy co najmniej 5 sekund audio
        if len(buffer) >= sample_rate * window_size:

            print("Analyzing window...")
            if np.max(np.abs(buffer)) < 0.01:
                continue
            else:
                fingerprints = generate_fingerprint(buffer, sr)
                song, score = match_fingerprints(fingerprints)

            if song and score > threshold:
                print("Song detected:", song)
                return {
                    "detected_song": song,
                    "score": score,
                    "confidence": round(score / len(fingerprints), 3)
                }

            # przesuwamy okno o 1 sekundę
            buffer = buffer[sample_rate:]

        # timeout
        if time.time() - start_time > max_seconds:
            print("Timeout reached.")
            return {
                "detected_song": None,
                "score": 0,
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
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #1f1f2e, #111);
                color: white;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }

            h1 {
                font-size: 3rem;
                margin-bottom: 40px;
                letter-spacing: 2px;
            }

            .circle {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                background: #1db954;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: 0.3s;
                box-shadow: 0 0 40px rgba(29,185,84,0.6);
            }

            .circle:hover {
                transform: scale(1.1);
            }

            .circle.listening {
                animation: pulse 1.2s infinite;
            }

            @keyframes pulse {
                0% { box-shadow: 0 0 20px rgba(29,185,84,0.6); }
                50% { box-shadow: 0 0 60px rgba(29,185,84,1); }
                100% { box-shadow: 0 0 20px rgba(29,185,84,0.6); }
            }

            #result {
                margin-top: 40px;
                font-size: 1.5rem;
                text-align: center;
            }

            .confidence {
                opacity: 0.7;
                font-size: 1rem;
            }
        </style>
    </head>
    <body>

        <h1>My song recognition</h1>

        <div class="circle" id="button" onclick="listen()">
            🎙
        </div>

        <div id="result"></div>

        <script>
            async function listen() {

                const button = document.getElementById("button");
                const result = document.getElementById("result");

                button.classList.add("listening");
                result.innerHTML = "Listening...";

                const response = await fetch("/listen", {
                    method: "POST"
                });

                const data = await response.json();

                button.classList.remove("listening");

                if (data.detected_song) {
                    result.innerHTML = 
                        "<b>" + data.detected_song + "</b><br>" +
                        "<span class='confidence'>Confidence: " + 
                        (data.confidence * 100).toFixed(1) + "%</span>";
                } else {
                    result.innerHTML = "No song detected";
                }
            }
        </script>

    </body>
    </html>
    """