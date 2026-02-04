# Django Bolt Test

High-performance REST API built with [Django Bolt](https://github.com/FarhanAliRaza/django-bolt)—async Python API framework on top of Django. Professional structure with JWT, pagination, search, permissions, health checks, WebSocket, and tests.

## Features

- **JWT authentication**: `POST /auth/login` → token; `GET /users/me` and `POST /users` require JWT
- **Health checks**: `GET /health` (liveness), `GET /ready` (readiness + DB)
- **Users API**: list (paginated, search), get by ID, current user (JWT), create (staff only)
- **Pagination**: `GET /users?page=1&page_size=10` (page-number)
- **Search**: `GET /users?search=...` (username filter)
- **Permissions**: `AllowAny` (list, get), `IsAuthenticated` + `IsStaff` (create user)
- **WebSocket**: `WS /ws` echo (text + JSON)
- **Server time headers**: `X-Server-Time`, `X-Response-Time` on every response
- **OpenAPI / Swagger**: `/docs`
- **Django Admin**: `/admin/`

## Tech Stack

- Python 3.13+
- Django 6.x
- [django-bolt](https://github.com/FarhanAliRaza/django-bolt) 0.5.x
- [msgspec](https://github.com/jcrist/msgspec) for schemas
- [uv](https://github.com/astral-sh/uv) for dependency management

## Project Structure

```
api/                 # Bolt API package (professional structure)
  __init__.py        # BoltAPI instance, middleware, register all routes
  middleware.py      # X-Server-Time, X-Response-Time headers
  routes/
    __init__.py      # register_all_routes(api)
    health.py        # /health, /ready
    auth.py          # POST /auth/login
    users.py         # GET/POST /users, /users/me
    websocket.py     # WS /ws
config/              # Django project
  api.py             # Re-export: from api import api (for runbolt autodiscovery)
  settings.py
  urls.py            # admin only
accounts/            # Django app
  schemas.py         # UserSchema, LoginSchema, TokenSchema, UserCreateSchema
  admin.py
  models.py
tests/               # Pytest: unit + integration (skip if server down)
  conftest.py        # require_server fixture
  test_health.py
  test_auth.py
  test_users.py
  test_websocket.py
  test_schemas.py
manage.py
pyproject.toml
requirements.txt
```

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Installation

```bash
git clone https://github.com/Matnazar-Matnazarov/django-bolt-test.git
cd django-bolt-test

uv venv
uv sync
# or: pip install -r requirements.txt
```

## Database

```bash
uv run manage.py migrate
uv run manage.py createsuperuser   # for admin & JWT login tests
```

## Run

```bash
uv run manage.py runbolt --dev --host localhost --port 8000
```

- **API**: http://localhost:8000  
- **Swagger**: http://localhost:8000/docs  
- **Admin**: http://localhost:8000/admin/

## API Endpoints

| Method | Path           | Description              | Auth        |
|--------|----------------|--------------------------|-------------|
| GET    | `/health`      | Liveness                  | No          |
| GET    | `/ready`       | Readiness (DB + checks)   | No          |
| POST   | `/auth/login`  | JWT token (body: username, password) | No  |
| GET    | `/users`       | List users (paginated, ?search=)    | No  |
| GET    | `/users/{id}`  | Get user by ID           | No          |
| GET    | `/users/me`    | Current user             | JWT         |
| POST   | `/users`       | Create user (staff only) | JWT + Staff |
| WS     | `/ws`          | Echo WebSocket            | No          |

**Response headers** (all): `X-Server-Time`, `X-Response-Time`.

**JWT:** send `Authorization: Bearer <access_token>`.

## Testing

**Unit tests** (no server):

```bash
uv run pytest tests/test_schemas.py -v
```

**Integration tests** (start server first):

```bash
uv run manage.py runbolt --dev --host localhost --port 8000 &
uv run pytest tests/ -v -m integration
# or: BASE_URL=http://localhost:8000 uv run pytest tests/ -v
```

**All tests** (integration tests skip automatically if server not running):

```bash
uv run pytest tests/ -v
# Unit tests run; integration tests skip with message if server is down
```

Optional dev deps: `uv sync --extra dev` (adds pytest, pytest-django, pytest-asyncio, httpx, websockets).

## Settings (optional)

In `config/settings.py`:

- `BOLT_JWT_SECRET` – JWT signing secret (default: `SECRET_KEY`)
- `BOLT_JWT_ALGORITHM` – default `"HS256"`
- `BOLT_JWT_EXPIRES_SECONDS` – default `3600`

## License

See [LICENSE](LICENSE).
