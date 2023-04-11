'''Request timing'''

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Request

from ..utils import benchmark


class TimingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        with benchmark.catchtime() as t:
            response = await call_next(request)

        response.headers["X-Response-Time"] = str(t.time)

        return response