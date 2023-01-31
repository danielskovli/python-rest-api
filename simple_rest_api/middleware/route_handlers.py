'''Custom route handlers'''

# Peewee has very poor type hinting support:
# pyright: reportUnknownVariableType=false
# pyright: reportMissingTypeArgument=false

import time
from typing import Callable, Coroutine, Any

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.routing import APIRoute

import peewee
from ..exceptions import ItemNotFoundError


class RequestTimingRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["X-Response-Time"] = str(duration)
            return response

        return custom_route_handler


class InterceptDbErrorRoute(RequestTimingRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)

            # TODO: Add additional db-exceptions as required
            except peewee.DoesNotExist as e:
                raise ItemNotFoundError(str(e))

        return custom_route_handler
