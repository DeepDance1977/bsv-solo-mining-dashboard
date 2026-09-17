"""
WebSocket Connection-Manager: haelt aktive Verbindungen und sendet Live-Updates
(Dashboard aktualisiert sich ohne Neuladen der Seite) an alle Clients.
"""
import asyncio
import json
import logging
from fastapi import WebSocket

logger = logging.getLogger("ws")


class ConnectionManager:
    def __init__(self):
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, event_type: str, payload: dict):
        message = json.dumps({"type": event_type, "data": payload}, default=str)
        dead = []
        async with self._lock:
            connections = list(self._connections)
        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    self._connections.discard(ws)


manager = ConnectionManager()
