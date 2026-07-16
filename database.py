"""
database.py
------------
Handles all SQLite database operations for the attendance system.

Why SQLite instead of CSV:
- Prevents duplicate/corrupted rows from concurrent writes
- Lets us query "has this person already been marked today?" reliably
- Easy to explain in an interview: proper schema > flat file
"""

import sqlite3
from datetime import datetime, date

DB_PATH = "attendance.db"


def get_connection():
    """Create (or reuse) a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """
    Creates the two tables we need:
    - users: one row per registered person, stores their face encoding
    - attendance: one row per attendance event, linked to users via user_id
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            encoding BLOB NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()


def add_user(name: str, encoding_bytes: bytes):
    """Insert a new registered user with their face encoding."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, encoding, created_at) VALUES (?, ?, ?)",
        (name, encoding_bytes, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_all_users():
    """Return all registered users (id, name, encoding)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, encoding FROM users")
    rows = cursor.fetchall()
    conn.close()
    return rows


def has_marked_attendance_today(user_id: int) -> bool:
    """
    Check if this user already has an attendance record for today.
    Prevents marking the same person present multiple times in one day.
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute(
        "SELECT 1 FROM attendance WHERE user_id = ? AND date = ?",
        (user_id, today)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


def mark_attendance(user_id: int):
    """Insert a new attendance record with current timestamp."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute(
        "INSERT INTO attendance (user_id, timestamp, date) VALUES (?, ?, ?)",
        (user_id, now.isoformat(), now.date().isoformat())
    )
    conn.commit()
    conn.close()


def get_today_attendance():
    """Return today's attendance joined with user names — used for display."""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("""
        SELECT users.name, attendance.timestamp
        FROM attendance
        JOIN users ON attendance.user_id = users.id
        WHERE attendance.date = ?
        ORDER BY attendance.timestamp
    """, (today,))
    rows = cursor.fetchall()
    conn.close()
    return rows
