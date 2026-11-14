import sqlite3
import hashlib
import secrets
import hmac
import uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta
import streamlit as st

DB_PATH = Path(__file__).resolve().parent / "portal.db"

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def connect():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                visited_at TEXT NOT NULL
            );
        """)

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"),
        bytes.fromhex(salt), 310000
    ).hex()

def register_user(username, email, password):
    username = username.strip()
    email = email.strip().lower()

    if len(username) < 3:
        return False, "Username must contain at least 3 characters."
    if "@" not in email or "." not in email:
        return False, "Enter a valid email address."
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    try:
        with connect() as conn:
            conn.execute(
                """INSERT INTO users
                (username, email, password_hash, salt, created_at)
                VALUES (?, ?, ?, ?, ?)""",
                (username, email, password_hash, salt, now())
            )
        return True, "Account created. You can now log in."
    except sqlite3.IntegrityError:
        return False, "That username or email is already registered."

def authenticate_user(username, password):
    with connect() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? COLLATE NOCASE",
            (username.strip(),)
        ).fetchone()

    if not user:
        return None

    calculated = hash_password(password, user["salt"])
    if not hmac.compare_digest(calculated, user["password_hash"]):
        return None

    return {"id": user["id"], "username": user["username"]}

def start_session(user_id):
    session_id = str(uuid.uuid4())
    timestamp = now()

    with connect() as conn:
        conn.execute(
            """INSERT INTO sessions
            (session_id, user_id, created_at, last_seen)
            VALUES (?, ?, ?, ?)""",
            (session_id, user_id, timestamp, timestamp)
        )
        conn.execute(
            """INSERT INTO visits (session_id, user_id, visited_at)
            VALUES (?, ?, ?)""",
            (session_id, user_id, timestamp)
        )

    return session_id

def touch_session(session_id):
    if not session_id:
        return
    with connect() as conn:
        conn.execute(
            "UPDATE sessions SET last_seen = ? WHERE session_id = ?",
            (now(), session_id)
        )

def end_session(session_id):
    if session_id:
        with connect() as conn:
            conn.execute(
                "DELETE FROM sessions WHERE session_id = ?",
                (session_id,)
            )

def is_authenticated():
    user_id = st.session_state.get("user_id")
    session_id = st.session_state.get("session_id")
    if not user_id or not session_id:
        return False
    touch_session(session_id)
    return True

def require_login():
    if not is_authenticated():
        st.warning("Please log in through the portal to access this page.")
        st.stop()

def logout():
    end_session(st.session_state.get("session_id"))
    for key in ("user_id", "username", "session_id"):
        st.session_state.pop(key, None)

def get_stats():
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=3)).isoformat(
        timespec="seconds"
    )
    with connect() as conn:
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        visits = conn.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
        active = conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE last_seen >= ?",
            (cutoff,)
        ).fetchone()[0]
    return users, visits, active
