"""WebSocket /ws echo endpoint (in-process WebSocketTestClient)."""

import pytest


@pytest.mark.asyncio
async def test_ws_echo(api):
    """WebSocket /ws echoes text back."""
    from django_bolt.testing import WebSocketTestClient

    async with WebSocketTestClient(api, "/ws") as ws:
        await ws.send_text("hello")
        reply = await ws.receive_text()
    assert "hello" in reply or "echo" in reply.lower()
