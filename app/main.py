import argparse
import librosa

from microphone import record_audio
from fingerprint import generate_fingerprint
from database import save_fingerprints, match_fingerprints


def index_song(file_path, song_name):
    print("Loading audio...")
    y, sr = librosa.load(file_path, mono=True)

    print("Generating fingerprints...")
    fingerprints = generate_fingerprint(y, sr)

    print(f"Generated {len(fingerprints)} fingerprints")

    print("Saving to database...")
    save_fingerprints(song_name, fingerprints)

    print("Done indexing!")


def listen_mode():
    print("Recording...")
    y, sr = record_audio(duration=5)

    fingerprints = generate_fingerprint(y, sr)

    song = match_fingerprints(fingerprints)

    if song:
        print("Detected song:", song)
    else:
        print("No match found")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shazam Clone CLI")

    parser.add_argument("--index", type=str, help="Path to song file to index")
    parser.add_argument("--name", type=str, help="Name of the song")
    parser.add_argument("--listen", action="store_true", help="Listen from microphone")

    args = parser.parse_args()

    if args.index and args.name:
        index_song(args.index, args.name)
    elif args.listen:
        listen_mode()
    else:
        print("Usage:")
        print("  python main.py --index path/to/song.mp3 --name \"Song Name\"")
        print("  python main.py --listen")
