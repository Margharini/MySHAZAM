import librosa
import numpy as np
import matplotlib.pyplot as plt

def analyze_audio(file_path):
    y, sr = librosa.load(file_path)

    # FFT
    fft = np.fft.fft(y)
    magnitude = np.abs(fft)

    frequencies = np.fft.fftfreq(len(magnitude), 1/sr)

    return frequencies, magnitude


if __name__ == "__main__":
    file_path = "C:/Users/User/Desktop/SHAZAM/samples/test.mp3"
    frequencies, magnitude = analyze_audio(file_path)

    plt.plot(frequencies[:5000], magnitude[:5000])
    plt.title("FFT Spectrum")
    plt.xlabel("Frequency")
    plt.ylabel("Magnitude")
    plt.show()
