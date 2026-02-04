"""WebSocket route: WS /ws echo."""

import json

from django_bolt.websocket import WebSocket


def register(api):
    """Register WebSocket route on the given BoltAPI."""

    @api.websocket("/ws")
    async def ws_echo(websocket: WebSocket):
        """Echo WebSocket: send back text and JSON."""
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                if not data:
                    continue
                try:
                    obj = json.loads(data)
                    await websocket.send_json({"echo": obj})
                except json.JSONDecodeError:
                    await websocket.send_text(f"Echo: {data}")
        except Exception:
            await websocket.close()
