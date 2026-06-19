"""
database/db.py
SQLite schema + CRUD layer for LifeMirror AI.
All tables: users, health_profile, mood_logs, journal_entries,
health_scores, predictions, recommendations.
"""
import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "lifemirror.db")


@contextmanager
def get_conn():
    """Context-managed SQLite connection with row factory."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create all tables if they do not exist."""
    with get_conn() as conn:
        c = conn.cursor()
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS health_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                age INTEGER, gender TEXT,
                height REAL, weight REAL, bmi REAL,
                sleep_hours REAL, water_intake REAL,
                exercise_minutes REAL, screen_time REAL,
                diet_type TEXT, smoking TEXT, alcohol TEXT,
                updated_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            CREATE TABLE IF NOT EXISTS mood_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mood TEXT, mood_score INTEGER,
                stress_level INTEGER, energy_level INTEGER,
                log_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                entry TEXT,
                sentiment REAL, polarity REAL, subjectivity REAL,
                emotion TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            CREATE TABLE IF NOT EXISTS health_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                physical REAL, mental REAL, lifestyle REAL,
                overall REAL,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                obesity REAL, diabetes REAL, hypertension REAL,
                sleep_disorder REAL, depression REAL, burnout REAL,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT, message TEXT, icon TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            """
        )


# ---------- USERS ----------
def create_user(username, email, password_hash):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (username,email,password_hash,created_at) VALUES (?,?,?,?)",
            (username, email, password_hash, datetime.utcnow().isoformat()),
        )


def get_user_by_username(username):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()
        return dict(row) if row else None


# ---------- HEALTH PROFILE ----------
def upsert_profile(user_id, data: dict):
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM health_profile WHERE user_id=?", (user_id,)
        ).fetchone()
        data["updated_at"] = datetime.utcnow().isoformat()
        cols = ",".join(data.keys())
        if existing:
            sets = ",".join(f"{k}=?" for k in data)
            conn.execute(
                f"UPDATE health_profile SET {sets} WHERE user_id=?",
                (*data.values(), user_id),
            )
        else:
            placeholders = ",".join("?" for _ in data)
            conn.execute(
                f"INSERT INTO health_profile (user_id,{cols}) VALUES (?,{placeholders})",
                (user_id, *data.values()),
            )


def get_profile(user_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM health_profile WHERE user_id=?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


# ---------- MOOD ----------
def add_mood(user_id, mood, mood_score, stress, energy):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO mood_logs (user_id,mood,mood_score,stress_level,energy_level,log_date) VALUES (?,?,?,?,?,?)",
            (user_id, mood, mood_score, stress, energy, datetime.utcnow().isoformat()),
        )


def get_moods(user_id, limit=60):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM mood_logs WHERE user_id=? ORDER BY log_date DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


# ---------- JOURNAL ----------
def add_journal(user_id, entry, sentiment, polarity, subjectivity, emotion):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO journal_entries (user_id,entry,sentiment,polarity,subjectivity,emotion,created_at) VALUES (?,?,?,?,?,?,?)",
            (user_id, entry, sentiment, polarity, subjectivity, emotion,
             datetime.utcnow().isoformat()),
        )


def get_journals(user_id, limit=60):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM journal_entries WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


# ---------- SCORES ----------
def save_scores(user_id, physical, mental, lifestyle, overall):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO health_scores (user_id,physical,mental,lifestyle,overall,created_at) VALUES (?,?,?,?,?,?)",
            (user_id, physical, mental, lifestyle, overall, datetime.utcnow().isoformat()),
        )


def get_scores(user_id, limit=30):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM health_scores WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


# ---------- PREDICTIONS ----------
def save_predictions(user_id, preds: dict):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO predictions
            (user_id,obesity,diabetes,hypertension,sleep_disorder,depression,burnout,created_at)
            VALUES (?,?,?,?,?,?,?,?)""",
            (user_id, preds["obesity"], preds["diabetes"], preds["hypertension"],
             preds["sleep_disorder"], preds["depression"], preds["burnout"],
             datetime.utcnow().isoformat()),
        )


# ---------- RECOMMENDATIONS ----------
def save_recommendation(user_id, category, message, icon):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO recommendations (user_id,category,message,icon,created_at) VALUES (?,?,?,?,?)",
            (user_id, category, message, icon, datetime.utcnow().isoformat()),
        )