"""
camera_manager.py
Utilidades para verificar conectividad antes de registrar una cámara.
Soporta: webcam local, HTTP (DroidCam/IP Webcam) y RTSP.
"""

import cv2
import urllib.request
import urllib.error


def test_camera(rtsp_url=0) -> dict:
    """
    Prueba la conectividad de una cámara y devuelve info básica.

    Parámetros
    ----------
    rtsp_url : int | str
        0 o "0"  → webcam local
        "http://..." → cámara WiFi HTTP (DroidCam, IP Webcam…)
        "rtsp://..." → stream RTSP

    Retorna
    -------
    dict con campos:
        success    bool
        message    str
        resolution str | None
        source     str  ("local" | "http" | "rtsp")
    """

    # ── Normalizar ──────────────────────────────────────────
    if rtsp_url in (0, "0"):
        source   = "local"
        cap_url  = 0
    elif str(rtsp_url).lower().startswith("http"):
        source   = "http"
        cap_url  = str(rtsp_url)
    else:
        source   = "rtsp"
        cap_url  = str(rtsp_url) + "?tcp"   # TCP más estable en WiFi

    # ── Para HTTP, chequeo rápido de disponibilidad ─────────
    if source == "http":
        try:
            urllib.request.urlopen(cap_url, timeout=3)
        except urllib.error.URLError as exc:
            return {
                "success":    False,
                "message":    f"No se pudo alcanzar la URL: {exc.reason}",
                "resolution": None,
                "source":     source,
            }

    # ── Intentar abrir con OpenCV ────────────────────────────
    cap = cv2.VideoCapture(
        cap_url,
        cv2.CAP_DSHOW if source == "local" else cv2.CAP_FFMPEG
    )
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        cap.release()
        return {
            "success":    False,
            "message":    "No se pudo abrir la cámara con OpenCV",
            "resolution": None,
            "source":     source,
        }

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        return {
            "success":    False,
            "message":    "La cámara se abrió pero no devolvió frames",
            "resolution": None,
            "source":     source,
        }

    h, w = frame.shape[:2]

    return {
        "success":    True,
        "message":    "Cámara conectada correctamente",
        "resolution": f"{w}x{h}",
        "source":     source,
    }
