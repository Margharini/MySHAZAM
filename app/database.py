from collections import defaultdict
from sqlalchemy import create_engine, text

import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:mp@localhost:5432/shazam"
)

engine = create_engine(DATABASE_URL)

def get_all_songs():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT DISTINCT song_name FROM fingerprints")
        )
        return [row[0] for row in result]

def save_fingerprints(song_name, fingerprints):
    with engine.connect() as conn:
        for hash_value, time_offset in fingerprints:
            conn.execute(
                text("INSERT INTO fingerprints (song_name, hash, time_offset) VALUES (:song, :hash, :offset)"),
                {"song": song_name, "hash": hash_value, "offset": time_offset}
            )
        conn.commit()

def match_fingerprints(fingerprints):

    if not fingerprints:
        return None, 0

    from collections import defaultdict

    # Wyciągamy wszystkie hashe z próbki
    sample_hashes = [h for h, _ in fingerprints]

    matches = []

    with engine.connect() as conn:

        # Jedno zapytanie z IN
        query = text("""
            SELECT song_name, time_offset, hash
            FROM fingerprints
            WHERE hash = ANY(:hashes)
        """)

        result = conn.execute(query, {"hashes": sample_hashes})

        # Mapujemy wyniki
        db_results = list(result)

    # Dopasowanie offsetów
    for db_song, db_offset, db_hash in db_results:

        for sample_hash, sample_offset in fingerprints:
            if sample_hash == db_hash:
                offset_diff = db_offset - sample_offset
                matches.append((db_song, offset_diff))

    if not matches:
        return None, 0

    counter = defaultdict(int)

    for song, diff in matches:
        counter[(song, diff)] += 1

    best_match = max(counter, key=counter.get)
    best_score = counter[best_match]

    return best_match[0], best_score

