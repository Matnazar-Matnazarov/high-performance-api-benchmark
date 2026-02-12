# Load Test (Go)

High-performance load test for **Django Bolt** and **DRF** API endpoints. Measures req/sec, success/fail counts, and latency percentiles (p50, p95, p99).

## Prerequisites

- [Go](https://go.dev/) 1.22+

## Build

```bash
cd loadtest
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

**Custom endpoints:**

```bash
./loadtest -api bolt -endpoints /health,/health/test,/ready,/users,/roles
./loadtest -api drf -endpoints /drf/health/,/drf/health/test/,/drf/ready/,/drf/users/,/drf/roles/
```

**Custom URL:**

```bash
./loadtest -api bolt -url http://localhost:8000 -duration 10s -concurrency 100
./loadtest -api drf -url http://localhost:8001 -duration 10s -concurrency 100
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `-api` | `bolt` | API type: `bolt` or `drf` |
| `-url` | bolt: 8000, drf: 8001 | Base URL |
| `-endpoints` | (per API) | Comma-separated endpoints |
| `-duration` | 5s | Test duration |
| `-concurrency` | 20 | Concurrent workers |

### Default endpoints

| API | Endpoints |
|-----|-----------|
| **bolt** | `/health`, `/health/test`, `/ready`, `/users`, `/roles` |
| **drf** | `/drf/health/`, `/drf/health/test/`, `/drf/ready/`, `/drf/users/`, `/drf/roles/` |

Workers are distributed across endpoints round-robin.

## Start servers first

```bash
# Terminal 1: Bolt (4 processes)
uv run manage.py runbolt --processes 4 --host localhost --port 8000

# Terminal 2: DRF (4 workers for load test; reduces fail rate)
uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8001 --workers 4

# Terminal 3: Load test
cd loadtest && ./loadtest -api bolt -duration 5s -concurrency 50
cd loadtest && ./loadtest -api drf -duration 5s -concurrency 50
```

> **Tip:** DRF with single worker causes high fail rate under load. Use `--workers 4` to match Bolt.

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
