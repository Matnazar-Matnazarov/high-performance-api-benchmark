"""API route modules: health, auth, roles, users, websocket."""

from api.routes import auth, health, roles, users, websocket


def register_all_routes(api):
    """Register all route modules on the given BoltAPI instance."""
    health.register(api)
    auth.register(api)
    roles.register(api)
    users.register(api)
    websocket.register(api)
