"""Database connection and initialization for ResumeFit AI.

Two backends are supported:

1. SQLite (default) -- a local file, used for local development. On most
   free hosting tiers (e.g. Render's free web service plan) the local disk
   is EPHEMERAL: it is wiped on every redeploy and on every restart caused
   by the free instance spinning down after ~15 minutes of inactivity. That
   is why accounts were "disappearing" -- the database file itself was
   being reset, not a frontend session-storage problem.

2. Postgres (production) -- used automatically whenever a DATABASE_URL
   environment variable is set (e.g. Render Postgres, Neon, Supabase all
   provide a free tier and hand you this connection string). Postgres runs
   as its own persistent service, so data survives web-service restarts
   and redeploys.

To keep the rest of the codebase (user_service.py) unchanged, the Postgres
path is wrapped in a small adapter that accepts the same '?' placeholder
style sqlite3 uses, and returns dict-like rows just like sqlite3.Row does.
"""

import os
from contextlib import contextmanager
from typing import Generator
from app.core.config import settings

_DEFAULT_DB_PATH = settings.DB_PATH

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras


def _normalized_pg_url(url: str) -> str:
    # Some providers (Render, Heroku) hand out "postgres://"; psycopg2 wants
    # "postgresql://".
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class _PGCursorAdapter:
    """Wraps a psycopg2 RealDictCursor so sqlite-style '?' placeholders work."""

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=()):
        self._cursor.execute(query.replace("?", "%s"), params)
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()


class _PGConnAdapter:
    """Wraps a psycopg2 connection to match the sqlite3.Connection surface
    that the rest of the app (user_service.py) relies on."""

    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return _PGCursorAdapter(
            self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        )

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


def init_db(db_path: str = None) -> None:
    """Initialize database tables if they do not exist."""
    if USE_POSTGRES:
        conn = psycopg2.connect(_normalized_pg_url(DATABASE_URL))
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    interests TEXT NOT NULL DEFAULT '[]',
                    onboarding_completed INTEGER NOT NULL DEFAULT 0,
                    resume_filename TEXT,
                    resume_skills TEXT NOT NULL DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
            # Safe migrations for pre-existing Postgres databases
            for col_def in [
                "resume_filename TEXT",
                "resume_skills TEXT NOT NULL DEFAULT '[]'",
            ]:
                cur.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col_def};")
            conn.commit()
            cur.close()
        finally:
            conn.close()
        return

    import sqlite3

    path = db_path or os.environ.get("RESUMEFIT_DB_PATH", _DEFAULT_DB_PATH)
    with sqlite3.connect(path) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                interests TEXT NOT NULL DEFAULT '[]',
                onboarding_completed INTEGER NOT NULL DEFAULT 0,
                resume_filename TEXT,
                resume_skills TEXT NOT NULL DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        # Run safe migrations for existing SQLite databases
        for col_def in ["resume_filename TEXT", "resume_skills TEXT NOT NULL DEFAULT '[]'"]:
            try:
                conn.execute(f"ALTER TABLE users ADD COLUMN {col_def};")
            except sqlite3.OperationalError:
                pass  # Column already exists
        conn.commit()


@contextmanager
def get_db_connection(db_path: str = None) -> Generator:
    """Context manager yielding a DB connection with dict-like row access.

    Uses Postgres when DATABASE_URL is set, otherwise falls back to the
    local SQLite file (dev only -- not persistent on most free hosts).
    """
    if USE_POSTGRES:
        raw_conn = psycopg2.connect(_normalized_pg_url(DATABASE_URL))
        conn = _PGConnAdapter(raw_conn)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return

    import sqlite3

    path = db_path or os.environ.get("RESUMEFIT_DB_PATH", _DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# Auto-initialize DB on import
init_db()
