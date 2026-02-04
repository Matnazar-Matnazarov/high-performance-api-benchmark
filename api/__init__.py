"""
API package – BoltAPI instance and route registration.

Structure:
  api/
    __init__.py   # BoltAPI, middleware, register all routes
    middleware.py # Server time / response time headers
    routes/
      health.py   # /health, /ready
      auth.py     # POST /auth/login
      users.py    # GET/POST /users, /users/me
      websocket.py # WS /ws
"""

from django_bolt import BoltAPI

from api.middleware import ServerTimeMiddleware
from api.routes import register_all_routes

api = BoltAPI(middleware=[ServerTimeMiddleware])
register_all_routes(api)
