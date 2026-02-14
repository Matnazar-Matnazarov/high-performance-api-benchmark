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
  <a href="https://github.com/Matnazar-Matnazarov/high-performance-api-benchmark/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/Matnazar-Matnazarov/high-performance-api-benchmark?style=for-the-badge" alt="License" height="28"/>
  </a>
</p>

<h1 align="center">High-Performance API Benchmark</h1>

<p align="center">
  <strong>Benchmark comparison</strong> of Django Bolt, DRF, FastAPI, Express.js, NestJS, Go, and Rust — same endpoints, load-tested for throughput and latency.
</p>

<p align="center">
  Django Bolt · DRF · FastAPI · Express · NestJS · Go · Rust · JWT · Health · WebSocket · OpenAPI/Swagger
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
| **DRF** | Django REST Framework at `/drf/` (JWT via SimpleJWT, same endpoints as Bolt) |
| **Docs** | OpenAPI/Swagger at `/docs` (JWT Authorize), Django Admin at `/admin/` |

---

## Tech Stack

| Technology | Role |
|------------|------|
| [Python](https://www.python.org/) 3.13+ | Runtime |
| [Django](https://www.djangoproject.com/) 6.x | Web framework |
| [Django Bolt](https://github.com/FarhanAliRaza/django-bolt) 0.5.x | Async API layer |
| [msgspec](https://github.com/jcrist/msgspec) | Schemas & serialization |
| [Django REST Framework](https://www.django-rest-framework.org/) | REST API (sync) |
| [djangorestframework-simplejwt](https://github.com/jazzband/djangorestframework-simplejwt) | JWT auth for DRF |
| [pytest](https://pytest.org/) | Testing (sync TestClient, no server required) |
| [uv](https://github.com/astral-sh/uv) | Dependency management |

---

## Project Structure

```
high-performance-api-benchmark/
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
├── api_drf/                     # DRF API (same endpoints as Bolt)
│   ├── serializers.py           # UserSerializer, UserCreateSerializer
│   ├── views.py                 # health, roles, users
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
├── src/                         # FastAPI (Bolt-compatible, port 8002, uvloop)
│   ├── main.py                  # app entry, lifespan
│   ├── config.py                # env, DB config
│   ├── database.py              # asyncpg pool
│   ├── middleware.py            # X-Server-Time, X-Response-Time
│   ├── routers/                 # health, roles, users
│   └── schemas/                 # Pydantic models
├── express/                     # Express.js (Bolt-compatible, port 8003)
│   ├── src/                     # index, config, db, middleware, routes
│   └── package.json
├── nest/                        # NestJS (Bolt-compatible, port 8004, Fastify)
│   ├── src/                     # modules: health, roles, users, auth
│   └── package.json
├── go/                          # Go API (Bolt-compatible, port 8005, Chi + pgx)
│   ├── main.go
│   └── internal/                # config, database, handlers, middleware
├── rust/                        # Rust API (Bolt-compatible, port 8006, Actix-web + sqlx)
│   ├── Cargo.toml
│   └── src/                     # main, config, db, middleware, handlers/
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
git clone https://github.com/Matnazar-Matnazarov/high-performance-api-benchmark.git
cd high-performance-api-benchmark

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

**DRF API** (sync, port 8001):
```bash
uv run uvicorn config.asgi:application --workers 4 --port 8001
```

**FastAPI** (Bolt-compatible, port 8002):
```bash
# Same endpoints as Bolt; uses asyncpg, same DB
uv run uvicorn src.main:app --host 0.0.0.0 --port 8002 --workers 4
```

**Express.js** (Bolt-compatible, port 8003):
```bash
cd express && npm install && npm start
# Same endpoints as Bolt; uses pg, same DB
```

**NestJS** (Bolt-compatible, port 8004, Fastify):
```bash
cd nest && npm install && npm run build && npm start
# Same endpoints as Bolt; Fastify + pg
```

**Go** (Bolt-compatible, port 8005, Chi + pgx):
```bash
cd go && go mod tidy && go run .
# Same endpoints as Bolt; pgx, same DB, Django password verify
# Port: GO_PORT env (default 8005). Use -url if different.
```

**Rust** (Bolt-compatible, port 8006, Actix-web + sqlx):
```bash
cd rust && cargo run --release
# Same endpoints as Bolt; sqlx, same DB, Django password verify
# Port: RUST_PORT env (default 8006).
```

| Resource | Bolt (8000) | DRF (8001) | FastAPI (8002) | Express (8003) | Nest (8004) | Go (8005) | Rust (8006) |
|----------|-------------|------------|----------------|----------------|-------------|-----------|-------------|
| API | http://localhost:8000 | http://localhost:8001/drf/ | http://localhost:8002 | http://localhost:8003 | http://localhost:8004 | http://localhost:8005 | http://localhost:8006 |
| Swagger | http://localhost:8000/docs | — | http://localhost:8002/docs | http://localhost:8003/docs | http://localhost:8004/docs | — | http://localhost:8006/swagger-ui/ |
| ReDoc | — | — | — | http://localhost:8003/redoc | — | — | — |
| Admin | http://localhost:8000/admin/ | http://localhost:8001/admin/ | — | — | — | — | — |

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

**DRF** (`/drf/` prefix, runserver 8001): same endpoints, JWT via SimpleJWT (`access`/`refresh` tokens).

**FastAPI** (port 8002): same endpoints as Bolt, asyncpg, same DB. For load test comparison.

**Express.js** (port 8003): same endpoints as Bolt, pg, same DB. For load test comparison.

**NestJS** (port 8004): same endpoints as Bolt, Fastify + pg. For load test comparison.

**Go** (port 8005): same endpoints as Bolt, Chi + pgx, Django password verify. For load test comparison.

**Rust** (port 8006): same endpoints as Bolt, Actix-web + sqlx, Django password verify. For load test comparison.

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

```bash
# Bolt (port 8000)
uv run manage.py runbolt --dev --host localhost --port 8000
uv run python scripts/load_test.py -a bolt -d 5 -c 50

# DRF (port 8001)
uv run manage.py runserver 8001
uv run python scripts/load_test.py -a drf -u http://localhost:8001 -d 5 -c 50

# FastAPI (port 8002)
uv run uvicorn src.main:app --host 0.0.0.0 --port 8002 --workers 4
uv run python scripts/load_test.py -a fastapi -u http://localhost:8002 -d 5 -c 50

# Express (port 8003) — use EXPRESS_WORKERS=4 for load test
cd express && EXPRESS_WORKERS=4 npm start
uv run python scripts/load_test.py -a express -u http://localhost:8003 -d 5 -c 50

# Nest (port 8004)
cd nest && npm run build && npm start
uv run python scripts/load_test.py -a nest -u http://localhost:8004 -d 5 -c 50

# Go (port 8005)
cd go && go run .
uv run python scripts/load_test.py -a go -u http://localhost:8005 -d 5 -c 50

# Rust (port 8006)
cd rust && cargo run --release
uv run python scripts/load_test.py -a rust -u http://localhost:8006 -d 5 -c 50
```

**Go loadtest** (faster, higher throughput, multi-endpoint):
```bash
cd loadtest
go build -o loadtest .
./loadtest -api bolt -duration 5s -concurrency 50
./loadtest -api drf -duration 5s -concurrency 50
./loadtest -api fastapi -duration 5s -concurrency 50
./loadtest -api express -duration 5s -concurrency 50
./loadtest -api nest -duration 5s -concurrency 50
./loadtest -api go -duration 5s -concurrency 50
./loadtest -api rust -duration 5s -concurrency 50
```

### Benchmark Results

Representative results (5s duration, 50 concurrent workers, endpoints: `/health`, `/health/test`, `/ready`, `/users`, `/roles`). Hardware and background load affect numbers.

| API | Req/sec | Success | Latency (ms) |
|-----|---------|---------|---------------|
| **Go** (Chi + pgx, port 8005) | ~60,000+ | 100% | p50≈0.8 · p95≈2 · p99≈5 |
| **Rust** (Actix-web + sqlx, port 8006) | ~14,000+ | 100% | p50≈2.7 · p95≈7 · p99≈18 |
| **Django-Bolt** (Django, 4 processes) | 9,816 | 100% | p50=4.3 · p95=11.4 · p99=16.5 |
| **Express** (Node.js, pg) | 4,068 | 100% | p50=11.6 · p95=17.1 · p99=23.5 |
| **Nest** (NestJS, Fastify + pg) | 3,879 | 100% | p50=12.0 · p95=18.5 · p99=27.1 |
| **FastAPI** (asyncpg, 4 workers) | 3,132 | 100% | p50=13.3 · p95=24.9 · p99=35.4 |
| **DRF** (Django async, 4 workers) | 725 | 87.4% | p50=63.6 · p95=117.1 · p99=162.3 |

> **Port alignment:** Go uses `GO_PORT` (default 8005), Rust uses `RUST_PORT` (default 8006). Use `-url` if the server runs on a different port.

| Option | Default | Description |
|--------|---------|-------------|
| `-a, --api` | `bolt` | API type: `bolt`, `drf`, `fastapi`, `express`, `nest`, `go`, or `rust` |
| `-u, --url` | bolt: 8000, drf: 8001, fastapi: 8002, express: 8003, nest: 8004, go: 8005, rust: 8006 | Base URL |
| `-d, --duration` | `5` (Python) / `5s` (Go) | Duration |
| `-c, --concurrency` | `20` | Concurrent workers |
| `-e, --endpoints` | (per API) | Comma-separated endpoints |

Go loadtest defaults: Bolt/FastAPI/Express/Nest/Go/Rust → `/health`, `/health/test`, `/ready`, `/users`, `/roles`; DRF → `/drf/health/`, `/drf/health/test/`, etc.

**Pytest integration tests** (servers must be running):

```bash
uv run pytest tests/test_load.py -v -m integration
```

---

## Settings (optional)

**Django** (`config/settings.py`):

| Setting | Default |
|---------|---------|
| `BOLT_JWT_SECRET` | `SECRET_KEY` |
| `BOLT_JWT_ALGORITHM` | `"HS256"` |
| `BOLT_JWT_EXPIRES_SECONDS` | `3600` |

**Go** (env / `.env`):

| Variable | Default |
|----------|---------|
| `GO_PORT` | 8005 |
| `BOLT_JWT_SECRET` | `SECRET_KEY` |
| `BOLT_JWT_EXPIRES_SECONDS` | 3600 |

**Rust** (env / `.env`):

| Variable | Default |
|----------|---------|
| `RUST_PORT` | 8006 |
| `BOLT_JWT_SECRET` | `SECRET_KEY` |
| `BOLT_JWT_EXPIRES_SECONDS` | 3600 |

---

## License

See [LICENSE](LICENSE).
