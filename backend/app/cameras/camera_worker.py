"""
app/cameras/camera_worker.py
"""

import cv2
import threading
import time
import logging
from pathlib import Path
from datetime import datetime

from ultralytics import YOLO
from app.events.event_manager import save_event

logger = logging.getLogger(__name__)

# BASE_DIR apunta a la raíz del proyecto (donde está main.py y la carpeta storage/)
# Estructura esperada:
#   backend/
#     main.py
#     storage/
#       snapshots/
#     app/
#       cameras/
#         camera_worker.py   ← este archivo (3 niveles abajo de backend/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Verificación en arranque para detectar rutas incorrectas rápidamente
_storage_dir = BASE_DIR / "storage" / "snapshots"
logger.info(f"Snapshots se guardarán en: {_storage_dir}")

# ─── Constantes ───────────────────────────────────────────────
FRAME_INTERVAL  = 0.033
AI_INTERVAL     = 0.5
SAVE_INTERVAL   = 10
RECONNECT_DELAY = 5
MAX_RECONNECTS  = 10
JPEG_QUALITY    = 80


class CameraWorker:

    def __init__(self, camera_id: int, name: str, rtsp_url):
        self.camera_id = camera_id
        self.name      = name
        self.rtsp_url  = self._parse_url(rtsp_url)

        self.cap     = None
        self._thread = None
        self._lock   = threading.Lock()
        self.running = False

        self._current_frame: bytes | None = None
        self._reconnect_count = 0
        self._last_ai_time    = 0.0
        self._last_save_time  = 0.0

        self.model = YOLO("yolov8n.pt")
        logger.info(f"[CAM {self.camera_id}] Worker creado → {self.rtsp_url!r}")

    @staticmethod
    def _parse_url(url):
        if url in (0, "0"):
            return 0
        return url

    def _open_capture(self) -> cv2.VideoCapture:
        url = self.rtsp_url

        if url == 0:
            # Intentar DSHOW primero, si falla usar MSMF (más estable en Windows)
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened():
                logger.warning(f"[CAM {self.camera_id}] DSHOW falló, intentando MSMF...")
                cap.release()
                cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
            if not cap.isOpened():
                logger.warning(f"[CAM {self.camera_id}] MSMF falló, intentando sin backend...")
                cap.release()
                cap = cv2.VideoCapture(0)
            if cap.isOpened():
                try:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                except Exception:
                    pass  # set() puede fallar en algunos drivers, no es crítico

        elif isinstance(url, str) and url.startswith("rtsp://"):
            cap = cv2.VideoCapture(url + "?tcp", cv2.CAP_FFMPEG)

        else:
            cap = cv2.VideoCapture(str(url), cv2.CAP_FFMPEG)

        if cap.isOpened():
            try:
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except Exception:
                pass

        return cap

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name=f"cam-{self.camera_id}"
        )
        self._thread.start()
        logger.info(f"[CAM {self.camera_id}] INICIADA")

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        logger.info(f"[CAM {self.camera_id}] DETENIDA")

    def _loop(self):
        while self.running:
            self.cap = self._open_capture()
            if not self.cap.isOpened():
                self._handle_reconnect("No se pudo abrir la cámara")
                continue

            logger.info(f"[CAM {self.camera_id}] Captura abierta OK")
            self._reconnect_count = 0

            while self.running:
                t0 = time.monotonic()
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    logger.warning(f"[CAM {self.camera_id}] Frame perdido")
                    break

                frame = self._run_ai(frame)
                self._encode_frame(frame)

                elapsed = time.monotonic() - t0
                sleep   = FRAME_INTERVAL - elapsed
                if sleep > 0:
                    time.sleep(sleep)

            self.cap.release()
        logger.info(f"[CAM {self.camera_id}] Loop terminado")

    def _handle_reconnect(self, reason: str):
        self._reconnect_count += 1
        logger.warning(
            f"[CAM {self.camera_id}] {reason}. "
            f"Reintento {self._reconnect_count}/{MAX_RECONNECTS} en {RECONNECT_DELAY}s…"
        )
        if self._reconnect_count >= MAX_RECONNECTS:
            logger.error(f"[CAM {self.camera_id}] Demasiados fallos. Deteniendo.")
            self.running = False
            return
        time.sleep(RECONNECT_DELAY)

    def _run_ai(self, frame):
        now = time.monotonic()
        if now - self._last_ai_time < AI_INTERVAL:
            return frame

        self._last_ai_time = now
        results = self.model(frame, verbose=False)

        for result in results:
            for box in result.boxes:
                cls        = int(box.cls[0])
                confidence = float(box.conf[0])
                if cls != 0 or confidence < 0.3:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    frame, f"Persona {confidence:.2f}",
                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 0), 2
                )
                self._maybe_save_event(frame, confidence)

        return frame

    def _maybe_save_event(self, frame, confidence: float):
        now = time.time()
        if now - self._last_save_time < SAVE_INTERVAL:
            return

        self._last_save_time = now
        timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_name = f"camera_{self.camera_id}_{timestamp}.jpg"

        # Ruta absoluta correcta — siempre relativa a BASE_DIR del proyecto
        image_path = BASE_DIR / "storage" / "snapshots" / image_name
        image_path.parent.mkdir(parents=True, exist_ok=True)

        cv2.imwrite(str(image_path), frame)

        # Guardar en BD como ruta relativa tipo "storage/snapshots/archivo.jpg"
        # Así el frontend puede construir la URL sin depender de la ruta absoluta de Windows
        relative_path = f"storage/snapshots/{image_name}"

        save_event(
            camera_name=self.name,
            event_type="Person Detected",
            confidence=confidence,
            image_path=relative_path   # ← relativa, no absoluta
        )
        logger.info(f"[CAM {self.camera_id}] Evento guardado → {image_name}")

    def _encode_frame(self, frame):
        ok, buf = cv2.imencode(
            ".jpg", frame,
            [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
        )
        if ok:
            with self._lock:
                self._current_frame = buf.tobytes()

    def get_frame(self) -> bytes | None:
        with self._lock:
            return self._current_frame