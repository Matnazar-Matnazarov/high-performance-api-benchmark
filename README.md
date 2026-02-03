# Django Bolt Test

High-performance REST API built with [Django Bolt](https://github.com/FarhanAliRaza/django-bolt)—async Python API framework on top of Django.

## Features

- **Async-first**: Django Bolt with async handlers and Django async ORM
- **OpenAPI / Swagger**: Interactive docs at `/docs` with response time headers
- **User API**: List users, get by ID, current user (`/users/me`) with auth check
- **Server time headers**: Every response includes `X-Server-Time` (UTC) and `X-Response-Time` (ms) for observability
- **Django Admin**: Admin at `/admin/` with session auth

## Tech Stack

- Python 3.13+
- Django 6.x
- [django-bolt](https://github.com/FarhanAliRaza/django-bolt) 0.5.x
- [msgspec](https://github.com/jcrist/msgspec) for schemas
- [uv](https://github.com/astral-sh/uv) for dependency management

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Installation

```bash
# Clone and enter project
git clone https://github.com/Matnazar-Matnazarov/django-bolt-test.git
cd django-bolt-test

# With uv (recommended)
uv venv
uv sync

# Or with pip
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Database

```bash
uv run manage.py migrate
uv run manage.py createsuperuser   # optional, for admin & /users/me
```

## Run

**Development (auto-reload):**

```bash
uv run manage.py runbolt --dev --host localhost --port 8000
```

**Production-style:**

```bash
uv run manage.py runbolt --host 0.0.0.0 --port 8000
```

- **API base**: http://localhost:8000  
- **Swagger UI**: http://localhost:8000/docs  
- **Django Admin**: http://localhost:8000/admin/

## API Endpoints

| Method | Path        | Description                    | Auth   |
|--------|-------------|--------------------------------|--------|
| GET    | `/users/`   | List all users                 | No     |
| GET    | `/users/{id}` | Get user by ID              | No     |
| GET    | `/users/me` | Current user (session)         | Yes    |

**Response headers** (all responses):

- `X-Server-Time`: UTC timestamp (ISO 8601)
- `X-Response-Time`: Request duration in milliseconds

**Example:** `GET /users/me` without session → `401` with `{"detail": "Authentication required"}`.

## Project Structure

```
config/           # Django project & Bolt API
  api.py          # BoltAPI routes (users), ServerTimeMiddleware
  middleware.py   # X-Server-Time, X-Response-Time headers
  settings.py
  urls.py
accounts/         # Django app (models, admin, schemas)
  schemas.py      # UserSchema (msgspec)
  urls.py         # Django URL routing
manage.py
pyproject.toml
requirements.txt
```

## Development

- Lint: `uv run ruff check .`
- Migrations: `uv run manage.py makemigrations`

## License

See [LICENSE](LICENSE).
