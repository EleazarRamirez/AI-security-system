import sqlite3
import logging
from pathlib import Path

from app.cameras.camera_registry import camera_registry

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = BASE_DIR / "storage" / "database" / "events.db"


class CameraService:

    @staticmethod
    def create_camera(name: str, rtsp_url: str) -> dict:
        conn   = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO cameras (name, rtsp_url)
            VALUES (?, ?)
        """, (name, rtsp_url))

        conn.commit()
        camera_id = cursor.lastrowid
        conn.close()

        url = 0 if rtsp_url == "0" else rtsp_url
        camera_registry.add_camera(camera_id, name, url)

        logger.info(f"Cámara creada id={camera_id} name={name!r}")
        return {"id": camera_id, "name": name, "rtsp_url": rtsp_url}

    @staticmethod
    def get_cameras() -> list[dict]:
        conn             = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor           = conn.cursor()
        cursor.execute("SELECT * FROM cameras ORDER BY id")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def delete_camera(camera_id: int) -> None:
        conn   = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cameras WHERE id = ?", (camera_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def load_cameras_from_db() -> None:
        cameras = CameraService.get_cameras()
        for cam in cameras:
            url = 0 if cam["rtsp_url"] == "0" else cam["rtsp_url"]
            camera_registry.add_camera(cam["id"], cam["name"], url)
            logger.info(f"Cámara restaurada id={cam['id']} name={cam['name']!r}")