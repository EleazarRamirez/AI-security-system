"""
app/api/routes.py
Endpoints FastAPI.

Rutas disponibles:
  POST   /cameras/test          → prueba conectividad antes de agregar
  POST   /cameras               → crea y arranca cámara
  GET    /cameras               → lista cámaras registradas
  GET    /cameras/{id}/stream   → stream MJPEG en vivo
  GET    /events                → últimos eventos detectados
"""

import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse

from app.cameras.camera_manager import test_camera
from app.cameras.camera_registry import camera_registry
from app.schemas.camera_schema import CameraCreate, CameraTest
from app.services.camera_service import CameraService
from app.events.event_manager import get_events

logger = logging.getLogger(__name__)

router = APIRouter()


# ══════════════════════════════════════════════════════════════
# CÁMARAS
# ══════════════════════════════════════════════════════════════

@router.post("/cameras/test")
def test_camera_endpoint(body: CameraTest):
    """
    Prueba si una cámara es accesible SIN agregarla al sistema.
    Útil para validar URLs antes de guardarlas.
    """
    result = test_camera(body.rtsp_url)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/cameras", status_code=201)
def create_camera(body: CameraCreate):
    """Registra una nueva cámara y arranca su worker."""
    camera = CameraService.create_camera(body.name, body.rtsp_url)
    return camera


@router.get("/cameras")
def list_cameras():
    """Lista todas las cámaras registradas."""
    return CameraService.get_cameras()


@router.get("/cameras/{camera_id}/stream")
async def stream_camera(camera_id: int):
    """
    Stream MJPEG en vivo de la cámara indicada.

    Consumir en HTML:
        <img src="/cameras/1/stream" />

    o con curl:
        curl http://localhost:8000/cameras/1/stream --output -
    """
    worker = camera_registry.get_camera(camera_id)

    if worker is None:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")

    async def frame_generator():
        boundary = b"--frame\r\n"
        header   = b"Content-Type: image/jpeg\r\n\r\n"

        while True:
            frame = worker.get_frame()

            if frame is None:
                # Esperar a que haya frames disponibles
                await asyncio.sleep(0.05)
                continue

            yield boundary + header + frame + b"\r\n"
            await asyncio.sleep(0.033)   # ~30 fps máx

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-cache"},
    )


@router.delete("/cameras/{camera_id}", status_code=204)
def delete_camera(camera_id: int):
    """Detiene y elimina una cámara."""
    worker = camera_registry.get_camera(camera_id)
    if worker is None:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")

    camera_registry.remove_camera(camera_id)
    CameraService.delete_camera(camera_id)
    return Response(status_code=204)


# ══════════════════════════════════════════════════════════════
# EVENTOS
# ══════════════════════════════════════════════════════════════

@router.get("/events")
def list_events(limit: int = 50, camera_name: str | None = None):
    """
    Retorna los últimos eventos detectados.
    Parámetros opcionales:
      limit       → máximo de registros (default 50)
      camera_name → filtrar por nombre de cámara
    """
    return get_events(limit=limit, camera_name=camera_name)
