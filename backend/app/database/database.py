import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

DATABASE_DIR = (
    BASE_DIR /
    "storage" /
    "database"
)

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE_PATH = DATABASE_DIR / "events.db"


def init_db():

    conn = sqlite3.connect(DATABASE_PATH)

    cursor = conn.cursor()

    # =========================
    # EVENTS
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            camera_name TEXT,

            event_type TEXT,

            confidence REAL,

            image_path TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # =========================
    # CAMERAS
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cameras (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            rtsp_url TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    conn.close()

    print("DATABASE INITIALIZED")