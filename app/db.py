import sqlite3, json, hashlib, time
from contextlib import contextmanager

DB_PATH = "promptshield.db"

@contextmanager
def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()

def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS requests (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ts          REAL NOT NULL,
            session_id  TEXT,
            prompt_hash TEXT NOT NULL,
            preview     TEXT NOT NULL,
            safe        INTEGER NOT NULL,
            blocked     INTEGER NOT NULL,
            stage       TEXT NOT NULL,       -- input | output | passed
            score       REAL NOT NULL,
            categories  TEXT NOT NULL,       -- JSON list
            source      TEXT,
            latency_ms  INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_req_ts      ON requests(ts);
        CREATE INDEX IF NOT EXISTS idx_req_session ON requests(session_id, ts);

        CREATE TABLE IF NOT EXISTS session_messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            ts         REAL NOT NULL,
            text       TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_sm_session ON session_messages(session_id, id);

        CREATE TABLE IF NOT EXISTS api_keys (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    key_hash  TEXT NOT NULL UNIQUE,
    name      TEXT NOT NULL,
    created   REAL NOT NULL,
    active    INTEGER NOT NULL DEFAULT 1
    );
        """)

def log_request(*, session_id, prompt, safe, blocked, stage, score,
                categories, source, latency_ms):
    with conn() as c:
        c.execute(
            "INSERT INTO requests (ts, session_id, prompt_hash, preview, safe, blocked,"
            " stage, score, categories, source, latency_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (time.time(), session_id,
             hashlib.sha256(prompt.encode()).hexdigest(), prompt[:200],
             int(safe), int(blocked), stage, score,
             json.dumps(categories), source, latency_ms))

def add_history(session_id: str, text: str, keep: int = 5):
    with conn() as c:
        c.execute("INSERT INTO session_messages (session_id, ts, text) VALUES (?,?,?)",
                  (session_id, time.time(), text[:2000]))
        c.execute("""DELETE FROM session_messages WHERE session_id = ? AND id NOT IN
                     (SELECT id FROM session_messages WHERE session_id = ?
                      ORDER BY id DESC LIMIT ?)""", (session_id, session_id, keep))

def get_history(session_id: str) -> list[str]:
    with conn() as c:
        rows = c.execute("SELECT text FROM session_messages WHERE session_id = ?"
                         " ORDER BY id", (session_id,)).fetchall()
    return [r["text"] for r in rows]