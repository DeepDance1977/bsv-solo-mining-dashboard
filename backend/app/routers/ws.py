"""
WebSocket-Endpunkt fuer Live-Updates des Dashboards (Node, Miner, System, Bloecke).
Authentifizierung erfolgt ueber ein JWT als Query-Parameter (?token=...), da
Browser-WebSockets keine benutzerdefinierten Header unterstuetzen.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from app.security import decode_token
from app.services.broadcaster import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    try:
        decode_token(token)
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket)
    try:
        while True:
            # Wir erwarten keine Client-Nachrichten, halten die Verbindung aber offen.
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
