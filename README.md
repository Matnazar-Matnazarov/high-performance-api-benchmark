<p align="center">
  <a href="https://www.djangoproject.com/" target="_blank">
    <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" height="28"/>
  </a>
  <a href="https://github.com/FarhanAliRaza/django-bolt" target="_blank">
    <img src="https://img.shields.io/badge/Django__Bolt-0.5.x-0C4A6E?style=for-the-badge&logo=lightning&logoColor=white" alt="Django Bolt" height="28"/>
  </a>
  <a href="https://www.python.org/" target="_blank">
    <img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.13+" height="28"/>
  </a>
  <a href="https://github.com/Matnazar-Matnazarov/django-bolt-test/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/Matnazar-Matnazarov/django-bolt-test?style=for-the-badge" alt="License" height="28"/>
  </a>
</p>

<h1 align="center">Django Bolt Test</h1>

<p align="center">
  <strong>High-performance REST API</strong> built with <a href="https://github.com/FarhanAliRaza/django-bolt">Django Bolt</a> — async Python API framework on top of Django.
</p>

<p align="center">
  JWT · Roles · Pagination · Search · Health checks · WebSocket · DRF · OpenAPI/Swagger · Tests
</p>

---

## Features

| Area | Description |
|------|-------------|
| **Auth** | JWT via `POST /auth/login`; `GET /users/me` and `POST /users` require JWT |
| **Health** | `GET /health` (liveness), `GET /ready` (readiness + DB) |
| **Users** | List (paginated, `?search=`), get by ID, current user, create (staff only) |
| **Pagination** | `GET /users?page=1&page_size=10` (page-number) |
| **Permissions** | `AllowAny` (list, get), `IsAuthenticated` + `IsStaff` (create user) |
| **WebSocket** | `WS /ws` echo (text + JSON) |
| **Observability** | `X-Server-Time`, `X-Response-Time` on every response |
| **DRF** | Django REST Framework at `/drf/` (async via adrf, Bolt-compatible JWT, same endpoints) |
| **Docs** | OpenAPI/Swagger at `/docs` (JWT Authorize), Django Admin at `/admin/` |

---

## Tech Stack

| Technology | Role |
|------------|------|
| [Python](https://www.python.org/) 3.13+ | Runtime |
| [Django](https://www.djangoproject.com/) 6.x | Web framework |
| [Django Bolt](https://github.com/FarhanAliRaza/django-bolt) 0.5.x | Async API layer |
| [msgspec](https://github.com/jcrist/msgspec) | Schemas & serialization |
| [Django REST Framework](https://www.django-rest-framework.org/) | REST API |
| [adrf](https://github.com/em1208/adrf) | Async DRF views & ViewSets |
| [djangorestframework-simplejwt](https://github.com/jazzband/djangorestframework-simplejwt) | JWT auth (SimpleJWT at `/auth/login/jwt/`) |
| [pytest](https://pytest.org/) | Testing (sync TestClient, no server required) |
| [uv](https://github.com/astral-sh/uv) | Dependency management |

---

## Project Structure

```
django-bolt-test/
├── api/                      # Bolt API package
│   ├── __init__.py            # BoltAPI instance, middleware, register routes
│   ├── middleware.py          # X-Server-Time, X-Response-Time
│   └── routes/
│       ├── __init__.py          # register_all_routes(api)
│       ├── health.py            # /health, /ready
│       ├── auth.py              # POST /auth/login
│       ├── roles.py             # GET /roles, GET /roles/code/{code}
│       ├── users.py             # GET/POST /users, /users/me
│       └── websocket.py         # WS /ws
├── api_drf/                     # DRF API async (adrf, same endpoints as Bolt)
│   ├── auth.py                  # BoltJWTAuthentication (access_token)
│   ├── serializers.py           # UserSerializer, UserCreateSerializer
│   ├── views.py                 # async health, roles, users, BoltLoginView
│   └── urls.py                  # /drf/...
├── config/                      # Django project
│   ├── api.py                   # Re-export: from api import api
│   ├── settings.py
│   └── urls.py                  # admin, drf
├── accounts/                    # Django app
│   ├── schemas.py               # UserSchema, RoleSchema, LoginSchema, TokenSchema, UserCreateSchema
│   ├── models.py                # User (AbstractUser), Role (TextChoices)
│   └── admin.py
├── tests/
│   ├── conftest.py              # api, client (TestClient), test_user, PostgreSQL teardown
│   ├── test_health.py, test_auth.py, test_users.py, test_roles.py
│   ├── test_drf.py              # DRF API tests
│   ├── test_schemas.py, test_websocket.py, test_load.py
│   └── ...
├── scripts/
│   └── load_test.py             # Load test (Python): req/sec, success/fail
├── loadtest/                    # Load test (Go): faster, higher throughput
│   ├── main.go
│   └── go.mod
├── assets/
│   └── django-bolt-logo.png     # Django Bolt branding
├── manage.py
├── pyproject.toml
└── requirements.txt
```

---

## Prerequisites

- **Python** 3.13+
- **[uv](https://github.com/astral-sh/uv)** (recommended) or pip

---

## Installation

```bash
git clone https://github.com/Matnazar-Matnazarov/django-bolt-test.git
cd django-bolt-test

uv venv
uv sync
# or: pip install -r requirements.txt
```

---

## Database

```bash
uv run manage.py migrate
uv run manage.py createsuperuser   # for admin & JWT login
```

---

## Run

**Bolt API** (async, port 8000):
```bash
uv run manage.py runbolt --dev --host localhost --port 8000
```

**DRF API** (async via adrf, port 8001):
```bash
# ASGI (recommended): uvicorn; use --workers 4 for load testing
uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8001 --workers 4

# or single worker (development)
uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8001

# or: Django runserver (WSGI)
uv run manage.py runserver 8001
```

| Resource | Bolt (8000) | DRF (8001) |
|----------|-------------|------------|
| API | http://localhost:8000 | http://localhost:8001/drf/ |
| Swagger | http://localhost:8000/docs | — |
| Admin | http://localhost:8000/admin/ | http://localhost:8001/admin/ |

---

## API Documentation (Swagger)

Interactive OpenAPI docs at `/docs` — Auth, Health, Users, WebSocket endpoints and schemas (LoginSchema, TokenSchema, UserSchema, UserCreateSchema).

**Authenticated requests in Swagger:**  
1. Call **POST /auth/login** with `username` and `password` to get `access_token`.  
2. Click **Authorize** (top right), enter `Bearer <your_access_token>` and confirm.  
3. Protected endpoints (e.g. **GET /users/me**, **POST /users**) will then send the token automatically.

<p align="center">
  <img src="swagger.png" alt="Swagger UI — Django Bolt Test API" width="800"/>
</p>

*Screenshot: Swagger UI at http://localhost:8000/docs*

---

## API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/health` | Liveness | — |
| GET | `/ready` | Readiness (DB + checks) | — |
| POST | `/auth/login` | JWT token (body: `username`, `password`) | — |
| GET | `/users` | List users (paginated, `?search=`) | — |
| GET | `/users/{id}` | Get user by ID | — |
| GET | `/users/me` | Current user | JWT |
| POST | `/users` | Create user (staff only) | JWT + Staff |
| WS | `/ws` | Echo WebSocket | — |

- **Response headers** (all): `X-Server-Time`, `X-Response-Time`.
- **JWT:** `Authorization: Bearer <access_token>`.

**DRF** (`/drf/` prefix, port 8001): same endpoints, async. Login `/auth/login/` returns Bolt format (`access_token`, `expires_in`, `token_type`). SimpleJWT at `/auth/login/jwt/`.

---

## Testing

Tests are written with **[pytest](https://pytest.org/)** (unit and integration). Unit tests need no server; integration tests call the live API and skip automatically if the server is not running (`require_server` fixture).

| Type | Command | Notes |
|------|---------|--------|
| **Unit** | `uv run pytest tests/test_schemas.py -v` | No server; schemas only |
| **Integration** | `uv run pytest tests/ -v -m integration` | Start server first |
| **All** | `uv run pytest tests/ -v` | Unit runs; integration skips if server down |

**Stack:** pytest, pytest-django, pytest-asyncio, httpx, websockets. Install dev deps: `uv sync --extra dev`.

---

## Load Test

Measures **req/sec**, **success** vs **fail** counts, and latency percentiles. Requires a running server.

**Python:**
```bash
# Bolt (port 8000)
uv run manage.py runbolt --processes 4 --host localhost --port 8000
uv run python scripts/load_test.py -a bolt -d 5 -c 50

# DRF (port 8001) — use uvicorn --workers 4 for load test
uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8001 --workers 4
uv run python scripts/load_test.py -a drf -u http://localhost:8001 -d 5 -c 50
```

**Go** (faster, higher throughput, multi-endpoint):
```bash
cd loadtest
go build -o loadtest .
./loadtest -api bolt -duration 5s -concurrency 50
./loadtest -api drf -duration 5s -concurrency 50
```

| Option | Default | Description |
|--------|---------|-------------|
| `-a, --api` | `bolt` | API type: `bolt` or `drf` |
| `-u, --url` | bolt: 8000, drf: 8001 | Base URL |
| `-d, --duration` | `5` (Python) / `5s` (Go) | Duration |
| `-c, --concurrency` | `20` | Concurrent workers |
| `-e, --endpoints` | (per API) | Comma-separated endpoints |

Go defaults: Bolt → `/health`, `/health/test`, `/ready`, `/users`, `/roles`; DRF → `/drf/health/`, `/drf/health/test/`, etc.

Pytest integration tests (servers must be running):

```bash
uv run pytest tests/test_load.py -v -m integration
```

---

## Settings (optional)

In `config/settings.py`:

| Setting | Default |
|---------|---------|
| `BOLT_JWT_SECRET` | `SECRET_KEY` |
| `BOLT_JWT_ALGORITHM` | `"HS256"` |
| `BOLT_JWT_EXPIRES_SECONDS` | `3600` |

---

## Troubleshooting

**PostgreSQL collation version mismatch** (warning when starting):

```
WARNING: database "bolt_test" has a collation version mismatch
DETAIL: The database was created using collation version 2.42, but the operating system provides version 2.43.
```

Fix (requires DB_USER with superuser or database owner):

```bash
uv run manage.py fix_db_collation
```

Or manually in `psql` (as superuser):

```sql
ALTER DATABASE bolt_test REFRESH COLLATION VERSION;
```

**DRF load test failures** (high fail rate): Run DRF with multiple workers to match Bolt:

```bash
uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8001 --workers 4
```

---

## License

See [LICENSE](LICENSE).
