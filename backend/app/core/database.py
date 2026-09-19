"""SQLite Database Connection and Initialization for ResumeFit AI."""

import os
import sqlite3
from contextlib import contextmanager
from typing import Generator
from app.core.config import settings

_DEFAULT_DB_PATH = settings.DB_PATH


def init_db(db_path: str = None) -> None:
    """Initialize database tables if they do not exist."""
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
def get_db_connection(db_path: str = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager yielding a SQLite connection with row_factory enabled."""
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
