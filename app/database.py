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
    hashes = list(set([hash_value for hash_value, _ in fingerprints]))

    if not hashes:
        return None, 0

    placeholders = ", ".join([f":h{i}" for i in range(len(hashes))])

    query = f"""
        SELECT song_name, COUNT(*) as match_count
        FROM fingerprints
        WHERE hash IN ({placeholders})
        GROUP BY song_name
        ORDER BY match_count DESC
        LIMIT 1
    """

    params = {f"h{i}": h for i, h in enumerate(hashes)}

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        row = result.fetchone()

        if row:
            return row[0], row[1]

    return None, 0

