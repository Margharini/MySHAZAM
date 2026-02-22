# 🎵 My Song Recognition

A simplified Shazam-like audio recognition system built with **FastAPI**, **PostgreSQL**, and **audio fingerprinting using STFT**.

This project demonstrates how digital signal processing, database indexing, and backend optimization can be combined to create a real-time music recognition system.

---

## Application Preview
![Application Screenshot](screenshot.png)

## 🚀 Key Features

- 🎤 Real-time recognition from microphone input
- 📂 Audio file identification
- 📥 Indexing new songs into a fingerprint database
- 🗄 Efficient SQL-based fingerprint matching
- 🌐 Minimal web interface
- ⚡ Backend performance optimizations

---

## 🧠 How It Works

### 1️⃣ Fingerprint Generation

Audio is processed using **Short-Time Fourier Transform (STFT)**:

- `n_fft = 2048`
- Spectral magnitude is computed per time frame
- Peaks above 50% of maximum magnitude are selected
- Peak frequency indices are converted into simple hash values

Each fingerprint is stored as:

```python
(hash_value, time_offset)
```

This is a simplified approach compared to production-grade fingerprinting systems.

### 2️⃣ Database Layer
Fingerprint storage schema:
```SQL
CREATE TABLE fingerprints (
    song_name TEXT,
    hash TEXT,
    time_offset INT
);
```

### 3️⃣ Matching Strategy

Instead of performing thousands of individual SQL queries, the system performs a single query:

```SQL
SELECT song_name, time_offset, hash
FROM fingerprints
WHERE hash = ANY(:hashes);
```

All potential matches are fetched at once.

The system then:

- Computes offset differences
- Counts consistent alignments
- Selects the song with the strongest offset consistency
This significantly improves performance and avoids request timeouts.

An index on the hash column is required for performance:

```SQL
CREATE INDEX idx_hash ON fingerprints(hash);
```

### 🎤Microphone Recording

Configuration:
- Sample rate: 44100 Hz
- Mono
- Float32 format
- Chunk size: 1024
- The /listen endpoint:
- Records 1-second chunks
- Builds a 5-second sliding window
- Attempts recognition
- Stops after 20 seconds (timeout)

Confidence score:

```python
confidence = score / number_of_sample_fingerprints
```

### API Endpoints
GET /
Returns a simple web interface with a microphone button.

GET /songs
Returns all indexed songs.

POST /index
Indexes a new uploaded song.

Parameters:
file: audio file
name: song name

Example response:
```JSON
{
  "status": "indexed",
  "fingerprints": 12345
}
```

POST /listen

Performs real-time recognition using the microphone.

Example response:
```JSON
{
  "detected_song": "Song Name",
  "score": 42,
  "confidence": 0.015
}
```

POST /identify

Identifies an uploaded audio file using the same fingerprinting and matching pipeline.

⚙ Installation
1. Clone the Repository
git clone <repository_url>
cd <project_directory>
2. Install Dependencies
pip install -r requirements.txt

Required libraries include:
- fastapi
- uvicorn
- librosa
- numpy
- scipy
- pyaudio
- sqlalchemy
- psycopg2

3. PostgreSQL Setup

Create database:
```cmd
createdb shazam
```

Create table:

```SQL
CREATE TABLE fingerprints (
    song_name TEXT,
    hash TEXT,
    time_offset INT
);
```

Create index for performance:

```SQL
CREATE INDEX idx_hash ON fingerprints(hash);
```

4. Run the Application
```cmd
uvicorn api:app --reload
```

Open in your browser:
```HTTP
http://127.0.0.1:8000
```

### ⚡ Performance Improvements
Initial version suffered from request timeouts due to thousands of database queries executed in loops.

Optimizations implemented:
- Replaced per-hash queries with a single ANY() query
- Added index on hash
- Introduced sliding recognition window
- Added silence detection before analysis
These improvements significantly reduced latency and eliminated timeouts.

### ⚠Limitations
- This is an educational implementation:
- Hashes are based only on peak frequency index
- No peak pairing
- No time-delta hashing
- Limited robustness to noise
- Confidence score is heuristic

Production systems use:
- Constellation maps
- Peak pairing
- Time-delta hashing
- Noise-resistant fingerprinting

🔮 Future Improvements
- Implement peak pairing and time-delta hashing
- Improve confidence scoring model
- Add background task processing
- Improve UI/UX
- Docker containerization
- Add automated tests

🎯 Project Goals
This project demonstrates:
- Digital Signal Processing fundamentals
- Audio fingerprinting techniques
- Efficient SQL-based matching strategies
- Backend API design with FastAPI
- Real-time audio handling
- Practical performance optimization
It serves as a technical exploration of simplified audio recognition systems.