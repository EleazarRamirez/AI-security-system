"""
app/websocket/connection_manager.py

Singleton del ConnectionManager de WebSocket.
Al estar en su propio módulo se evita el import circular:
  event_manager → main → event_manager
"""

import asyncio
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket conectado. Total: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("WebSocket desconectado. Total: %d", len(self.active_connections))

    async def broadcast(self, data: dict):
        """Envía un dict JSON a todos los clientes conectados."""
        dead: list[WebSocket] = []
        for ws in self.active_connections:
            try:
                await ws.send_json(data)
            except Exception as exc:
                logger.warning("Error enviando a WebSocket: %s", exc)
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


# Singleton accesible desde cualquier módulo
manager = ConnectionManager()
