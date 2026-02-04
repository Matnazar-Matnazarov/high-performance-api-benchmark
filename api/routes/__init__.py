"""API route modules: health, auth, users, websocket."""

from api.routes import auth, health, users, websocket


def register_all_routes(api):
    """Register all route modules on the given BoltAPI instance."""
    health.register(api)
    auth.register(api)
    users.register(api)
    websocket.register(api)
