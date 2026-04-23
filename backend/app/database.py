"""SQLite connection management, schema initialization, and vocab seeding.

The database file defaults to ``backend/korean_vocab.db`` and can be
overridden via the ``DATABASE_PATH`` environment variable.

Two kinds of data live here:

- A cached copy of the seed vocabulary from :mod:`app.vocab_data` (table
  ``vocab``). This lets test generation run in pure SQL and keeps an
  auditable snapshot of what the user was practicing at the time.
- Test history: ``tests`` (one row per test session) and ``questions``
  (one row per question, including the graded answer after submission).
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from app.vocab_data import VOCAB

DB_PATH = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(__file__), "..", "korean_vocab.db"),
)


def get_connection() -> sqlite3.Connection:
    """Open a new SQLite connection with recommended pragmas."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    """Context manager yielding a connection that commits/rolls back."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS vocab (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    korean       TEXT NOT NULL UNIQUE,
    romanization TEXT NOT NULL,
    english      TEXT NOT NULL,
    level        TEXT NOT NULL,
    category     TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_vocab_level ON vocab(level);

CREATE TABLE IF NOT EXISTS tests (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at  TEXT,
    level         TEXT NOT NULL,
    mode          TEXT NOT NULL,  -- 'written' | 'listening' | 'mixed'
    num_questions INTEGER NOT NULL,
    score         INTEGER,        -- number correct, filled in on submit
    total         INTEGER         -- total questions (denormalized for listing)
);

CREATE TABLE IF NOT EXISTS questions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id         INTEGER NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    position        INTEGER NOT NULL,
    question_type   TEXT NOT NULL,
    vocab_id        INTEGER NOT NULL REFERENCES vocab(id),
    prompt          TEXT NOT NULL,
    correct_answer  TEXT NOT NULL,
    options_json    TEXT,          -- JSON array for multiple-choice, else NULL
    user_answer     TEXT,
    is_correct      INTEGER        -- 0/1, NULL until graded
);

CREATE INDEX IF NOT EXISTS idx_questions_test ON questions(test_id);
"""


def init_db() -> None:
    """Create tables if they don't exist and seed/refresh the vocab list."""
    with get_db() as conn:
        conn.executescript(SCHEMA)
        _seed_vocab(conn)


def _seed_vocab(conn: sqlite3.Connection) -> None:
    """Upsert the curated vocabulary list from :mod:`app.vocab_data`."""
    rows = [
        (v["korean"], v["romanization"], v["english"], v["level"], v["category"])
        for v in VOCAB
    ]
    conn.executemany(
        """
        INSERT INTO vocab (korean, romanization, english, level, category)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(korean) DO UPDATE SET
            romanization = excluded.romanization,
            english      = excluded.english,
            level        = excluded.level,
            category     = excluded.category
        """,
        rows,
    )
