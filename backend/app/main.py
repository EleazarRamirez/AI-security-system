print("MAIN PY CARGADO CORRECTAMENTE")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.database.database import init_db
from app.websocket.connection_manager import manager   # ← módulo propio (evita import circular)

# =========================
# APP
# =========================

app = FastAPI()

# =========================
# DATABASE
# =========================

init_db()

# =========================
# STARTUP: restaurar cámaras guardadas en BD
# =========================

@app.on_event("startup")
async def on_startup():
    from app.services.camera_service import CameraService
    CameraService.load_cameras_from_db()
    print("CÁMARAS RESTAURADAS DESDE BD")

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# STORAGE (archivos estáticos / snapshots)
# =========================

app.mount(
    "/storage",
    StaticFiles(directory="storage"),
    name="storage"
)

# =========================
# ROUTES
# =========================

app.include_router(router)

# =========================
# WEBSOCKET
# =========================

@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()   # mantiene la conexión viva
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/test-ws")
async def test_ws():
    return {"message": "websocket route exists"}
