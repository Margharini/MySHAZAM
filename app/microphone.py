import pyaudio
import numpy as np

def record_audio(duration=5, rate=44100):
    chunk = 1024
    format = pyaudio.paFloat32
    channels = 1

    p = pyaudio.PyAudio()

    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    print("Recording...")

    frames = []

    for _ in range(int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(np.frombuffer(data, dtype=np.float32))

    stream.stop_stream()
    stream.close()
    p.terminate()

    return np.hstack(frames), rate
