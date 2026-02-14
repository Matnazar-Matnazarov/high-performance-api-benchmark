# Load Test (Go)

High-performance load test for **Django Bolt**, **DRF**, **FastAPI**, and **Express.js** API endpoints. Measures req/sec, success/fail counts, and latency percentiles (p50, p95, p99).

## Prerequisites

- [Go](https://go.dev/) 1.22+

## Build

From project root:
```bash
cd loadtest
go build -o loadtest .
```

Or if already in `loadtest/`:
```bash
go build -o loadtest .
```

## Usage

**Django Bolt** (port 8000):

```bash
./loadtest -api bolt -duration 5s -concurrency 50
```

**DRF** (port 8001):

```bash
./loadtest -api drf -duration 5s -concurrency 50
```

**FastAPI** (port 8002):

```bash
./loadtest -api fastapi -duration 5s -concurrency 50
```

**Express.js** (port 8003):

```bash
./loadtest -api express -duration 5s -concurrency 50
```

**NestJS** (port 8004):

```bash
./loadtest -api nest -duration 5s -concurrency 50
```

**Custom endpoints:**

```bash
./loadtest -api bolt -endpoints /health,/health/test,/ready,/users,/roles
./loadtest -api drf -endpoints /drf/health/,/drf/health/test/,/drf/ready/,/drf/users/,/drf/roles/
./loadtest -api fastapi -endpoints /health,/health/test,/ready,/users,/roles
./loadtest -api express -endpoints /health,/health/test,/ready,/users,/roles
./loadtest -api nest -endpoints /health,/health/test,/ready,/users,/roles
```

**Custom URL:**

```bash
./loadtest -api bolt -url http://localhost:8000 -duration 10s -concurrency 100
./loadtest -api drf -url http://localhost:8001 -duration 10s -concurrency 100
./loadtest -api fastapi -url http://localhost:8002 -duration 10s -concurrency 100
./loadtest -api express -url http://localhost:8003 -duration 10s -concurrency 100
./loadtest -api nest -url http://localhost:8004 -duration 10s -concurrency 100
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `-api` | `bolt` | API type: `bolt`, `drf`, `fastapi`, `express`, or `nest` |
| `-url` | bolt: 8000, drf: 8001, fastapi: 8002, express: 8003, nest: 8004 | Base URL |
| `-endpoints` | (per API) | Comma-separated endpoints |
| `-duration` | 5s | Test duration |
| `-concurrency` | 20 | Concurrent workers |

### Default endpoints

| API | Endpoints |
|-----|-----------|
| **bolt** | `/health`, `/health/test`, `/ready`, `/users`, `/roles` |
| **drf** | `/drf/health/`, `/drf/health/test/`, `/drf/ready/`, `/drf/users/`, `/drf/roles/` |
| **fastapi** | `/health`, `/health/test`, `/ready`, `/users`, `/roles` |
| **express** | `/health`, `/health/test`, `/ready`, `/users`, `/roles` |
| **nest** | `/health`, `/health/test`, `/ready`, `/users`, `/roles` |

Workers are distributed across endpoints round-robin.

## Start servers first

```bash
# Terminal 1: Bolt (4 processes)
uv run manage.py runbolt --processes 4 --host localhost --port 8000

# Terminal 2: DRF (4 workers for load test; reduces fail rate)
uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8001 --workers 4

# Terminal 3: FastAPI (optional; same endpoints as Bolt)
uv run uvicorn src.main:app --host 0.0.0.0 --port 8002 --workers 4

# Terminal 4: Express (4 workers for load test; reduces fail rate)
cd express && EXPRESS_WORKERS=4 npm start

# Terminal 5: NestJS (optional; same endpoints as Bolt)
cd nest && npm run build && npm start

# Terminal 6: Load test
cd loadtest && ./loadtest -api bolt -duration 5s -concurrency 50
cd loadtest && ./loadtest -api drf -duration 5s -concurrency 50
cd loadtest && ./loadtest -api fastapi -duration 5s -concurrency 50
cd loadtest && ./loadtest -api express -duration 5s -concurrency 50
cd loadtest && ./loadtest -api nest -duration 5s -concurrency 50
```

> **Tip:** DRF with single worker and Express with single process cause high fail rate under load. Use `--workers 4` for DRF and `EXPRESS_WORKERS=4` for Express to match Bolt.

## Sample output

```
Load test: BOLT @ http://localhost:8000
  Endpoints: /health, /health/test, /ready, /users, /roles
  Duration: 5s | Concurrency: 50
--------------------------------------------------
Total requests:  12500
Success (2xx):   12400
Fail:            100
Success rate:   99.2%
Fail rate:      0.8%
Requests/sec:   2500.0
Latency (ms):   p50=15.2 p95=45.3 p99=78.1
```
