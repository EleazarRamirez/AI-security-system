"""
app/events/event_manager.py
"""

import asyncio
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_PATH = (
    BASE_DIR / "storage" / "database" / "events.db"
)


# =========================
# SAVE EVENT
# =========================

def save_event(
    camera_name: str,
    event_type: str,
    confidence: float,
    image_path: str
):
    conn   = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO events (camera_name, event_type, confidence, image_path, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (camera_name, event_type, round(confidence, 4), image_path, created_at))

    conn.commit()
    conn.close()
    logger.info("Evento guardado en SQLite")

    # =========================
    # WEBSOCKET — thread-safe
    # =========================
    # save_event se llama desde un hilo secundario (CameraWorker).
    # asyncio.create_task() solo funciona desde el event loop principal.
    # run_coroutine_threadsafe() es la forma correcta.

    try:
        from app.websocket.connection_manager import manager   # import aquí para evitar circular

        event_data = {
            "camera_name": camera_name,
            "event_type":  event_type,
            "confidence":  round(confidence * 100, 1),
            "image_path":  image_path.replace("\\", "/"),
            "created_at":  created_at,
        }

        loop = asyncio.get_event_loop()

        if loop.is_running():
            # ✅ Correcto: programa la coroutine desde un hilo externo
            asyncio.run_coroutine_threadsafe(
                manager.broadcast(event_data),
                loop
            )
        else:
            logger.warning("Event loop no disponible; notificación WebSocket omitida")

    except Exception as exc:
        logger.error("Error notificando por WebSocket: %s", exc)


# =========================
# GET EVENTS
# =========================

def get_events(limit: int = 50, camera_name: str | None = None) -> list[dict]:
    """
    Retorna los últimos eventos.
    - limit       → máximo de registros
    - camera_name → filtro opcional por nombre de cámara   ← CORREGIDO (antes ignorado)
    """
    conn             = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor           = conn.cursor()

    if camera_name:
        cursor.execute("""
            SELECT * FROM events
            WHERE camera_name = ?
            ORDER BY id DESC
            LIMIT ?
        """, (camera_name, limit))
    else:
        cursor.execute("""
            SELECT * FROM events
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
