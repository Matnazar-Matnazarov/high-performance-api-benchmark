# Go API (Bolt-compatible)

Django-Bolt endpointlariga mos professional Go API. Chi router, pgx, Django password verify.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | — | Liveness check |
| GET | `/health/test` | — | Custom health check |
| GET | `/ready` | — | Readiness (DB check) |
| POST | `/auth/login` | — | JWT (username, password) |
| GET | `/roles` | — | List all roles |
| GET | `/roles/code/{code}` | — | Role by code |
| GET | `/users` | — | List users (search, role, pagination) |
| GET | `/users/{user_id}` | — | User by ID |
| GET | `/users/me` | JWT | Current user |
| POST | `/users` | JWT + Staff | Create user |
| GET | `/swagger-ui/` | — | Swagger UI (OpenAPI docs) |
| GET | `/api-docs/openapi.json` | — | OpenAPI 3.0 spec |

## Response headers

Every response includes:
- `X-Server-Time` — UTC timestamp
- `X-Response-Time` — response duration (ms)

## Quick start

```bash
cd go
go mod tidy
go run .
```

**Default port:** 8005

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `GO_PORT` | 8005 | Server port |
| `DB_NAME` | bolt_test | PostgreSQL database |
| `DB_USER` | postgres | PostgreSQL user |
| `DB_PASSWORD` | — | PostgreSQL password |
| `DB_HOST` | localhost | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `BOLT_JWT_SECRET` | SECRET_KEY | JWT signing secret |
| `BOLT_JWT_EXPIRES_SECONDS` | 3600 | JWT expiry (seconds) |

Load from `.env` in project root.

## Load test

```bash
# Terminal 1: Start Go API
cd go && go run .

# Terminal 2: Run loadtest
cd loadtest && go build -o loadtest . && ./loadtest -api go -duration 5s -concurrency 50
```

If Go runs on a different port, use `-url`:
```bash
./loadtest -api go -url http://localhost:8003 -duration 5s -concurrency 50
```

## Database

Uses Django `accounts_user` table. Login verifies Django password hashes (pbkdf2_sha256) via [unchained](https://github.com/alexandrevicenzi/unchained).
