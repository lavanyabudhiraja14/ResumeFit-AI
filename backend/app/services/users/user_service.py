"""User repository and service operations for ResumeFit AI."""

import json
import uuid
from typing import Optional, Dict, Any, List
from app.core.database import get_db_connection


def _format_user_row(row: Any) -> Dict[str, Any]:
    """Converts a SQLite row into a clean user dict with typed fields."""
    raw_interests = row["interests"] if "interests" in row.keys() else "[]"
    try:
        interests_list = json.loads(raw_interests) if isinstance(raw_interests, str) else list(raw_interests)
    except Exception:
        interests_list = []

    raw_resume_skills = row["resume_skills"] if "resume_skills" in row.keys() else "[]"
    try:
        resume_skills_list = json.loads(raw_resume_skills) if isinstance(raw_resume_skills, str) else list(raw_resume_skills)
    except Exception:
        resume_skills_list = []

    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "password_hash": row["password_hash"] if "password_hash" in row.keys() else "",
        "interests": interests_list,
        "onboarding_completed": bool(row["onboarding_completed"]),
        "resume_filename": row["resume_filename"] if "resume_filename" in row.keys() else None,
        "resume_skills": resume_skills_list,
        "created_at": str(row["created_at"]) if "created_at" in row.keys() else None,
        "updated_at": str(row["updated_at"]) if "updated_at" in row.keys() else None,
    }


def get_user_by_email(email: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve user by normalized email."""
    normalized_email = email.strip().lower()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? LIMIT 1;", (normalized_email,))
        row = cursor.fetchone()
        if row:
            return _format_user_row(row)
    return None


def get_user_by_id(user_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve user by unique user ID."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ? LIMIT 1;", (user_id,))
        row = cursor.fetchone()
        if row:
            return _format_user_row(row)
    return None


def create_user(
    name: str,
    email: str,
    password_hash: str,
    interests: Optional[List[str]] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new user with empty or initial interests."""
    user_id = str(uuid.uuid4())
    normalized_email = email.strip().lower()
    interests_json = json.dumps(interests or [])
    onboarding_completed = 1 if (interests and len(interests) > 0) else 0

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (id, name, email, password_hash, interests, onboarding_completed)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (user_id, name.strip(), normalized_email, password_hash, interests_json, onboarding_completed),
        )
        conn.commit()

    return get_user_by_id(user_id, db_path)


def update_user_interests(
    user_id: str,
    interests: List[str],
    mark_onboarding_completed: bool = True,
    db_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Update user's interests and update onboarding completion status."""
    interests_json = json.dumps(interests)
    onboarding_val = 1 if mark_onboarding_completed else 0

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET interests = ?,
                onboarding_completed = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (interests_json, onboarding_val, user_id),
        )
        conn.commit()

    return get_user_by_id(user_id, db_path)


def update_user_resume(
    user_id: str,
    filename: str,
    skills: List[str],
    db_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Persist user's uploaded resume filename and extracted skills."""
    skills_json = json.dumps(skills)

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET resume_filename = ?,
                resume_skills = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (filename, skills_json, user_id),
        )
        conn.commit()

    return get_user_by_id(user_id, db_path)

