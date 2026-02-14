#!/usr/bin/env python3
"""
Load test script for API endpoints.

Measures: req/sec, success count, fail count, success rate.

Bolt (runbolt): uv run manage.py runbolt --dev --host localhost --port 8000
DRF (uvicorn): uv run uvicorn config.asgi:application --port 8001
FastAPI (uvicorn): uv run uvicorn src.main:app --port 8002
Express: cd express && npm start (port 8003)

Usage:
    uv run python scripts/load_test.py --api bolt
    uv run python scripts/load_test.py --api drf -u http://localhost:8001
    uv run python scripts/load_test.py --api fastapi -u http://localhost:8002
    uv run python scripts/load_test.py --api express -u http://localhost:8003
"""

import argparse
import asyncio
import time
from dataclasses import dataclass, field

import httpx


@dataclass
class LoadResult:
    """Single request result."""

    success: bool
    status_code: int | None
    latency_ms: float
    error: str | None = None


@dataclass
class LoadStats:
    """Aggregated load test statistics."""

    total: int = 0
    success: int = 0
    fail: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.success / self.total) * 100

    @property
    def fail_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.fail / self.total) * 100

    def req_per_sec(self, duration_sec: float) -> float:
        if duration_sec <= 0:
            return 0.0
        return self.total / duration_sec


async def single_request(
    client: httpx.AsyncClient,
    url: str,
    method: str = "GET",
    **kwargs,
) -> LoadResult:
    """Perform one HTTP request and return LoadResult."""
    start = time.perf_counter()
    try:
        resp = await client.request(method, url, **kwargs)
        latency_ms = (time.perf_counter() - start) * 1000
        ok = 200 <= resp.status_code < 300
        return LoadResult(
            success=ok, status_code=resp.status_code, latency_ms=latency_ms
        )
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        return LoadResult(
            success=False,
            status_code=None,
            latency_ms=latency_ms,
            error=str(e),
        )


async def worker(
    client: httpx.AsyncClient,
    base_url: str,
    endpoint: str,
    queue: asyncio.Queue,
    stop_event: asyncio.Event,
):
    """Worker that continuously hits the endpoint until stop_event is set."""
    url = f"{base_url.rstrip('/')}{endpoint}"
    while not stop_event.is_set():
        result = await single_request(client, url)
        try:
            queue.put_nowait(result)
        except asyncio.QueueFull:
            pass


async def run_load_test(
    base_url: str,
    endpoints: list[str],
    duration_sec: float,
    concurrency: int,
) -> tuple[LoadStats, list[float]]:
    """
    Run load test: spawn workers for each endpoint, collect results for duration_sec.
    Returns (LoadStats, latencies).
    """
    stats = LoadStats()
    latencies: list[float] = []
    queue: asyncio.Queue[LoadResult] = asyncio.Queue(maxsize=100_000)
    stop_event = asyncio.Event()

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Distribute workers across endpoints round-robin
        workers = [
            asyncio.create_task(
                worker(
                    client, base_url, endpoints[i % len(endpoints)], queue, stop_event
                )
            )
            for i in range(concurrency)
        ]

        # Collector: read from queue until duration expires
        end_time = time.perf_counter() + duration_sec

        async def collect():
            nonlocal stats, latencies
            while time.perf_counter() < end_time:
                try:
                    result = await asyncio.wait_for(queue.get(), timeout=0.5)
                    stats.total += 1
                    if result.success:
                        stats.success += 1
                        latencies.append(result.latency_ms)
                    else:
                        stats.fail += 1
                        if result.error and len(stats.errors) < 20:
                            stats.errors.append(result.error)
                except asyncio.TimeoutError:
                    continue

        collector = asyncio.create_task(collect())
        await asyncio.sleep(duration_sec)
        stop_event.set()
        await asyncio.gather(*workers)
        await asyncio.sleep(0.2)
        collector.cancel()
        try:
            await collector
        except asyncio.CancelledError:
            pass

    return stats, latencies


BOLT_DEFAULTS = {
    "url": "http://localhost:8000",
    "endpoints": "/health,/health/test,/ready,/users,/roles",
}
DRF_DEFAULTS = {
    "url": "http://localhost:8001",
    "endpoints": "/drf/health/,/drf/health/test/,/drf/ready/,/drf/users/,/drf/roles/",
}
FASTAPI_DEFAULTS = {
    "url": "http://localhost:8002",
    "endpoints": "/health,/health/test,/ready,/users,/roles",
}
EXPRESS_DEFAULTS = {
    "url": "http://localhost:8003",
    "endpoints": "/health,/health/test,/ready,/users,/roles",
}
NEST_DEFAULTS = {
    "url": "http://localhost:8004",
    "endpoints": "/health,/health/test,/ready,/users,/roles",
}
API_DEFAULTS = {
    "bolt": BOLT_DEFAULTS,
    "drf": DRF_DEFAULTS,
    "fastapi": FASTAPI_DEFAULTS,
    "express": EXPRESS_DEFAULTS,
    "nest": NEST_DEFAULTS,
}


def main():
    parser = argparse.ArgumentParser(
        description="Load test API endpoints. Measures req/sec, success/fail counts."
    )
    parser.add_argument(
        "-a",
        "--api",
        choices=["bolt", "drf", "fastapi", "express", "nest"],
        default="bolt",
        help="API type (bolt, drf, fastapi, express, nest)",
    )
    parser.add_argument(
        "-u",
        "--url",
        default=None,
        help="Base URL (overrides default for --api)",
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=float,
        default=5.0,
        help="Test duration in seconds (default: 5)",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=20,
        help="Concurrent workers (default: 20)",
    )
    parser.add_argument(
        "-e",
        "--endpoints",
        default=None,
        help="Comma-separated endpoints (overrides default for --api)",
    )
    args = parser.parse_args()

    defaults = API_DEFAULTS.get(args.api, BOLT_DEFAULTS)
    base_url = args.url or defaults["url"]
    endpoints_str = args.endpoints or defaults["endpoints"]
    endpoints = [p.strip() for p in endpoints_str.split(",") if p.strip()]
    if not endpoints:
        endpoints = ["/health"]

    print(f"Load test: {args.api.upper()} @ {base_url}")
    print(f"  Endpoints: {endpoints}")
    print(f"  Duration: {args.duration}s | Concurrency: {args.concurrency}")
    print("-" * 50)

    stats, latencies = asyncio.run(
        run_load_test(base_url, endpoints, args.duration, args.concurrency)
    )

    elapsed = args.duration
    rps = stats.req_per_sec(elapsed)

    print(f"Total requests:  {stats.total}")
    print(f"Success (2xx):  {stats.success}")
    print(f"Fail:           {stats.fail}")
    print(f"Success rate:   {stats.success_rate:.1f}%")
    print(f"Fail rate:      {stats.fail_rate:.1f}%")
    print(f"Requests/sec:   {rps:.1f}")
    if latencies:
        latencies.sort()
        n = len(latencies)

        def _percentile_idx(p: int) -> int:
            return max(0, min(int((n - 1) * p / 100), n - 1)) if n else 0

        p50 = latencies[_percentile_idx(50)]
        p95 = latencies[_percentile_idx(95)]
        p99 = latencies[_percentile_idx(99)]
        print(f"Latency (ms):   p50={p50:.1f} p95={p95:.1f} p99={p99:.1f}")
    if stats.errors:
        print("\nSample errors (max 5):")
        for e in stats.errors[:5]:
            print(f"  - {e[:80]}")


if __name__ == "__main__":
    main()
