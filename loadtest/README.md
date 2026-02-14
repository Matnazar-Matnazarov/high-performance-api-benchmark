# Load Test (Go)

High-performance load test for **Django Bolt**, **DRF**, **FastAPI**, **Express.js**, **NestJS**, **Go**, and **Rust** API endpoints. Measures req/sec, success/fail counts, and latency percentiles (p50, p95, p99).

## Prerequisites

- [Go](https://go.dev/) 1.22+

## Build

From project root:
```bash
cd loadtest
go mod tidy
go build -o loadtest .
```

Or if already in `loadtest/`:
```bash
go build -o loadtest .
```

## Usage

| API | Port | Command |
|-----|------|---------|
| **Bolt** | 8000 | `./loadtest -api bolt -duration 5s -concurrency 50` |
| **DRF** | 8001 | `./loadtest -api drf -duration 5s -concurrency 50` |
| **FastAPI** | 8002 | `./loadtest -api fastapi -duration 5s -concurrency 50` |
| **Express** | 8003 | `./loadtest -api express -duration 5s -concurrency 50` |
| **Nest** | 8004 | `./loadtest -api nest -duration 5s -concurrency 50` |
| **Go** | 8005 | `./loadtest -api go -duration 5s -concurrency 50` |
| **Rust** | 8006 | `./loadtest -api rust -duration 5s -concurrency 50` |

**Custom URL** (if server runs on different port):
```bash
./loadtest -api go -url http://localhost:8003 -duration 5s -concurrency 50
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
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `-api` | bolt | API type: `bolt`, `drf`, `fastapi`, `express`, `nest`, `go`, `rust` |
| `-url` | (per API) | Base URL. bolt:8000, drf:8001, fastapi:8002, express:8003, nest:8004, go:8005, rust:8006 |
| `-endpoints` | (per API) | Comma-separated endpoints |
| `-duration` | 5s | Test duration |
| `-concurrency` | 20 | Concurrent workers |

## Start servers first

Ensure the target API is running before load test:

```bash
# Bolt
uv run manage.py runbolt --processes 4 --host localhost --port 8000

# DRF (4 workers recommended)
uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8001 --workers 4

# FastAPI
uv run uvicorn src.main:app --host 0.0.0.0 --port 8002 --workers 4

# Express (4 workers recommended)
cd express && EXPRESS_WORKERS=4 npm start

# Nest
cd nest && npm run build && npm start

# Go (default port 8005)
cd go && go run .

# Rust (default port 8006)
cd rust && cargo build --release && cargo run --release
```

> **Rust:** Agar `rustup` xato bersa, `rustup default stable` bajarib toolchain o'rnating.
> **Tip:** If load test shows 100% fail rate, verify the server is running on the expected port. Use `-url` to override.

## Sample output

```
Load test: GO @ http://localhost:8005
  Endpoints: /health, /health/test, /ready, /users, /roles
  Duration: 5s | Concurrency: 50
--------------------------------------------------
Total requests:  125000
Success (2xx):   125000
Fail:            0
Success rate:   100.0%
Fail rate:      0.0%
Requests/sec:   25000.0
Latency (ms):   p50=1.2 p95=3.5 p99=8.1
```
