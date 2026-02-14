"""Run DRF API server (uvicorn). Usage: uv run drf [--port 8001]"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Run DRF API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8001, help="Port")
    parser.add_argument("--workers", type=int, default=4, help="Workers")
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
        "config.asgi:application",
        host=args.host,
        port=args.port,
        workers=args.workers,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
