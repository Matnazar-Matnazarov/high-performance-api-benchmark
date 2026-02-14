# Express.js API (Bolt-compatible)

Node.js/Express API with same endpoints as Django Bolt. Uses PostgreSQL (same DB as Django). X-Server-Time, X-Response-Time on every response.

## Prerequisites

- Node.js 20+
- PostgreSQL (same DB as Django: `bolt_test`)

## Install

```bash
cd express
npm install
```

## Run

```bash
npm start
# or: node src/index.js
# or: EXPRESS_PORT=8003 node src/index.js
```

Default port: **8003**

## API Docs

| Doc | URL |
|-----|-----|
| **Swagger UI** | http://localhost:8003/docs (0.0.0.0 avtomatik localhost ga redirect) |
| **ReDoc** | http://localhost:8003/redoc |
| **Scalar** | http://localhost:8003/scalar |
| **OpenAPI JSON** | http://localhost:8003/openapi.json |

Use **Authorize** in Swagger/Scalar to add `Bearer <access_token>` from POST /auth/login.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| GET | `/health/test` | Custom health check |
| GET | `/ready` | Readiness (DB check) |
| GET | `/roles` | List roles |
| GET | `/roles/code/:code` | Get role by code |
| GET | `/users` | List users (paginated, `?search=`, `?role=`) |
| GET | `/users/:id` | Get user by ID |
| POST | `/auth/login` | JWT token (body: `username`, `password`) |

## Load Test

Use **4 workers** to reduce fail rate (like Bolt/DRF):

**Python:**
```bash
cd express && EXPRESS_WORKERS=4 npm start &
uv run python scripts/load_test.py -a express -u http://localhost:8003 -d 5 -c 50
```

**Go:**
```bash
cd express && EXPRESS_WORKERS=4 npm start &
cd loadtest && ./loadtest -api express -duration 5s -concurrency 50
```

Or: `npm run start:cluster`

## Env vars (same as Django)

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `BOLT_JWT_SECRET` or `SECRET_KEY` (JWT signing)
- `EXPRESS_PORT` (default: 8003)
