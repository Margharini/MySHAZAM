# My Song Recognition

A minimal Shazam-like song recognition system built with FastAPI, PostgreSQL, and audio fingerprinting using STFT.

The application can:

Recognize songs in real time from a microphone

Index new songs into a database

Identify uploaded audio files

Provide a simple web interface

## Application Preview
![Application Screenshot](screenshot.png)
## Overview

This project implements a simplified audio fingerprinting pipeline. It demonstrates how digital signal processing and database matching can be combined to build a basic music recognition system.

The system:

Extracts spectral features from audio using Short-Time Fourier Transform (STFT).

Detects spectral peaks per time frame.

Converts peak frequency indices into simple hashes.

Stores hashes with time offsets in PostgreSQL.

Matches incoming audio fingerprints against stored fingerprints using offset alignment.

## Architecture
### Fingerprint Generation

Audio is transformed using STFT (n_fft=2048).

For each time frame, peaks above 50% of the maximum magnitude are detected.

Each peak frequency index becomes a fingerprint hash.

Each fingerprint is stored as:

```python
(hash_value, time_offset)
```

This is a simplified approach compared to production-grade fingerprinting systems.

### Database Layer
Table Structure
```SQL
CREATE TABLE fingerprints (
    song_name TEXT,
    hash TEXT,
    time_offset INT
);
```

###Matching Strategy

Instead of performing thousands of individual SQL queries, the system performs a single query:

```SQL
SELECT song_name, time_offset, hash
FROM fingerprints
WHERE hash = ANY(:hashes);
```

All potential matches are fetched at once. Offset differences are then counted to determine the most consistent alignment, which identifies the best matching song.

An index on the hash column is required for performance:

```SQL
CREATE INDEX idx_hash ON fingerprints(hash);
```

### Microphone Recording

- Sample rate: 44100 Hz
- Mono
- Float32 format
- Chunk size: 1024
- The /listen endpoint:
- Records 1-second chunks
- Builds a 5-second sliding window
- Attempts recognition
- Stops after 20 seconds (timeout)

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

Confidence is calculated as:

```python
confidence = score / number_of_sample_fingerprints
```

POST /identify

Identifies an uploaded audio file using the same fingerprinting and matching pipeline.

Installation
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

3. Set Up PostgreSQL

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

### Performance Improvements
The system originally suffered from request timeouts due to thousands of database queries executed in a loop.
This was resolved by:
Replacing per-hash queries with a single ANY() query
Adding a database index on hash
Using a sliding window for recognition
Adding silence detection before analysis
These changes significantly reduced latency and eliminated timeouts.

### Limitations
This is a simplified fingerprinting implementation:
Hashes are based only on peak frequency index
No peak pairing
No time-delta hashing
Limited robustness to noise
Confidence score is heuristic, not probabilistic
Production systems use constellation maps, peak pairing, and noise-resistant hashing techniques.

### Future Improvements
Implement peak pairing and time-delta hashing
Improve confidence scoring logic
Add background processing tasks
Improve UI/UX
Add containerization (Docker)
Add automated tests
Project Goals
This project demonstrates:
Digital signal processing fundamentals
Audio fingerprinting concepts
Efficient SQL-based matching
API design with FastAPI
Real-time audio handling
Backend performance optimization
It serves as an educational implementation of a simplified music recognition system.

