# Rust API (Bolt-compatible)

Django-Bolt endpointlariga mos professional Rust API. Actix-web, sqlx, djangohashers.

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
| GET | `/swagger-ui/` | — | Swagger UI (OpenAPI docs) |

## Response headers

Every response includes:
- `X-Server-Time` — UTC timestamp
- `X-Response-Time` — response duration (ms)

## Quick start

```bash
cd rust
cargo build --release
cargo run --release
```

**Default port:** 8006

**Swagger UI:** http://localhost:8006/swagger-ui/

> Agar `rustup could not choose a version` xato bersa: `rustup default stable` bajarib toolchain o'rnating.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `RUST_PORT` | 8006 | Server port |
| `DB_NAME` | bolt_test | PostgreSQL database |
| `DB_USER` | postgres | PostgreSQL user |
| `DB_PASSWORD` | — | PostgreSQL password |
| `DB_HOST` | localhost | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_POOL_SIZE` | 32 | Connection pool size (load test uchun 32+) |
| `BOLT_JWT_SECRET` | SECRET_KEY | JWT signing secret |
| `BOLT_JWT_EXPIRES_SECONDS` | 3600 | JWT expiry (seconds) |

Load from `.env` in project root.

## Load test

```bash
# Terminal 1: Start Rust API
cd rust && cargo build --release && cargo run --release

# Terminal 2: Build va run loadtest
cd loadtest && go mod tidy && go build -o loadtest . && ./loadtest -api rust -duration 5s -concurrency 50
```

## Project structure

```
rust/
├── Cargo.toml
├── rust-toolchain.toml
└── src/
    ├── main.rs           # App entry, routes, AppState, Swagger UI
    ├── config.rs         # Env config (DB, JWT, port)
    ├── db.rs             # PostgreSQL pool
    ├── middleware.rs     # X-Server-Time, X-Response-Time
    ├── openapi.rs        # OpenAPI/Swagger spec
    └── handlers/
        ├── mod.rs         # Re-exports
        ├── health.rs      # /health, /health/test, /ready
        ├── auth.rs        # POST /auth/login
        ├── roles.rs       # GET /roles, /roles/code/{code}
        └── users.rs       # GET /users, /users/{id}
```

## Database

Uses Django `accounts_user` table. Login verifies Django password hashes (pbkdf2_sha256) via [djangohashers](https://docs.rs/djangohashers).
