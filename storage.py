"""SQLite storage and local account services."""

import hashlib
import hmac
import json
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


def default_database_path():
    """Store app data in a small folder in the user's home directory."""
    folder = Path.home() / ".medical_symptom_simulator"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "simulator.sqlite3"


class Database:
    def __init__(self, path=None):
        self.path = Path(path) if path else default_database_path()
        self.initialize()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=15)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self):
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    display_name TEXT NOT NULL,
                    salt BLOB NOT NULL,
                    password_hash BLOB NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                    age INTEGER,
                    notes TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at TEXT NOT NULL,
                    symptoms_json TEXT NOT NULL,
                    severity INTEGER NOT NULL,
                    duration_days INTEGER NOT NULL,
                    vitals_json TEXT NOT NULL,
                    assessment_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_sessions_user_date
                    ON sessions(user_id, created_at DESC);
                """
            )

    def register(self, username, display_name, password):
        username = username.strip()
        display_name = display_name.strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,32}", username):
            raise ValueError("Username must be 3-32 letters, numbers, dots, dashes, or underscores.")
        if not display_name:
            raise ValueError("Enter a display name.")
        if len(password) < 8:
            raise ValueError("Password must have at least 8 characters.")
        salt = os.urandom(16)
        password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 240_000)
        created_at = datetime.now().astimezone().isoformat(timespec="seconds")
        try:
            with self.connect() as connection:
                cursor = connection.execute(
                    "INSERT INTO users(username, display_name, salt, password_hash, created_at) VALUES(?,?,?,?,?)",
                    (username, display_name, salt, password_hash, created_at),
                )
                user_id = cursor.lastrowid
                connection.execute("INSERT INTO profiles(user_id) VALUES(?)", (user_id,))
        except sqlite3.IntegrityError as error:
            raise ValueError("That username is already taken.") from error
        return {"id": user_id, "username": username, "display_name": display_name}

    def authenticate(self, username, password):
        with self.connect() as connection:
            user = connection.execute("SELECT * FROM users WHERE username=?", (username.strip(),)).fetchone()
        if not user:
            raise ValueError("Username or password was not recognized.")
        supplied_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), user["salt"], 240_000)
        if not hmac.compare_digest(supplied_hash, user["password_hash"]):
            raise ValueError("Username or password was not recognized.")
        return {"id": user["id"], "username": user["username"], "display_name": user["display_name"]}

    def get_profile(self, user_id):
        with self.connect() as connection:
            row = connection.execute("SELECT age, notes FROM profiles WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else {"age": None, "notes": ""}

    def save_profile(self, user_id, age, notes):
        if age is not None and not 0 <= age <= 125:
            raise ValueError("Age must be between 0 and 125.")
        with self.connect() as connection:
            connection.execute(
                "UPDATE profiles SET age=?, notes=? WHERE user_id=?",
                (age, notes.strip(), user_id),
            )

    def save_session(self, user_id, symptoms, severity, duration_days, vitals, assessment):
        created_at = datetime.now().astimezone().isoformat(timespec="minutes")
        with self.connect() as connection:
            cursor = connection.execute(
                """INSERT INTO sessions
                (user_id, created_at, symptoms_json, severity, duration_days, vitals_json, assessment_json)
                VALUES(?,?,?,?,?,?,?)""",
                (user_id, created_at, json.dumps(symptoms), severity, duration_days,
                 json.dumps(vitals), json.dumps(assessment)),
            )
            session_id = cursor.lastrowid
        return {
            "id": session_id, "created_at": created_at, "symptoms": symptoms,
            "severity": severity, "duration_days": duration_days, "vitals": vitals,
            "assessment": assessment,
        }

    def get_sessions(self, user_id, limit=100):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM sessions WHERE user_id=? ORDER BY id DESC LIMIT ?",
                (user_id, max(1, min(limit, 500))),
            ).fetchall()
        sessions = []
        for row in rows:
            sessions.append({
                "id": row["id"], "created_at": row["created_at"],
                "symptoms": json.loads(row["symptoms_json"]),
                "severity": row["severity"], "duration_days": row["duration_days"],
                "vitals": json.loads(row["vitals_json"]),
                "assessment": json.loads(row["assessment_json"]),
            })
        return sessions

    def session_count(self, user_id):
        with self.connect() as connection:
            return connection.execute("SELECT COUNT(*) FROM sessions WHERE user_id=?", (user_id,)).fetchone()[0]

