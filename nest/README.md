# NestJS API (Bolt-compatible)

NestJS + Fastify + pg. Same endpoints as Django Bolt. Port 8004.

## Prerequisites

- Node.js 20+
- PostgreSQL (same DB as Django)

## Install & Run

```bash
cd nest
npm install
npm run build
npm start
```

**EADDRINUSE (port 8004 band)?** Avvalgi processni to'xtating:
```bash
npm run stop
# yoki: pkill -f "node.*dist/main"
```

## Endpoints

| Path | Method | Description |
|------|--------|-------------|
| `/health` | GET | Liveness |
| `/health/test` | GET | Custom health check |
| `/ready` | GET | Readiness (DB) |
| `/roles` | GET | List roles |
| `/roles/code/:code` | GET | Get role by code |
| `/users` | GET | List users (paginated, search, role filter) |
| `/users/:id` | GET | Get user by ID |
| `/auth/login` | POST | Login (JWT) |
| `/docs` | GET | Swagger UI |

## Env

Same as Express. Load from project root `.env`:

- `NEST_PORT` (default: 8004)
- `NEST_HOST` (default: 0.0.0.0)
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `BOLT_JWT_SECRET`, `BOLT_JWT_EXPIRES_SECONDS`

## Load Test

```bash
# Terminal 1
cd nest && npm run build && npm start

# Terminal 2
cd loadtest && ./loadtest -api nest -duration 5s -concurrency 50
```

## Tech

- **Fastify** — faster than Express
- **pg** — PostgreSQL, same pool config as Express
- **Swagger** — `/docs` built-in
- **JWT** — Django PBKDF2 password verification
