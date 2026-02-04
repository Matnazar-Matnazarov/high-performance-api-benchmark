"""WebSocket /ws echo endpoint tests."""

import pytest

try:
    import websockets
except ImportError:
    websockets = None


@pytest.mark.integration
@pytest.mark.skipif(websockets is None, reason="websockets package not installed")
@pytest.mark.asyncio
async def test_ws_echo(require_server):
    """WebSocket /ws echoes text back (requires running server)."""
    ws_url = require_server.replace("http://", "ws://").replace("https://", "wss://")
    try:
        async with websockets.connect(f"{ws_url}/ws", open_timeout=2.0) as ws:
            await ws.send("hello")
            reply = await ws.recv()
    except (OSError, ConnectionRefusedError):
        pytest.skip(
            "API server not running. Start: "
            "uv run manage.py runbolt --dev --host localhost --port 8000"
        )
    assert "hello" in reply or "echo" in reply.lower()
