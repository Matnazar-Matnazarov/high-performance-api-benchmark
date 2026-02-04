"""Bolt API middleware: server time and response time headers."""

import time
from datetime import datetime

from django.utils import timezone


class ServerTimeMiddleware:
    """
    Adds X-Server-Time (UTC) and X-Response-Time (ms) to every response.
    Visible in Swagger UI when executing a request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    async def __call__(self, request):
        start = time.perf_counter()
        response = await self.get_response(request)
        duration_ms = (time.perf_counter() - start) * 1000
        utc = getattr(timezone, "UTC", timezone.UTC)
        server_time = datetime.now(utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        response.headers["X-Server-Time"] = server_time
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        return response
