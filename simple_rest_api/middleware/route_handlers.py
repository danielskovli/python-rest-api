'''Custom route handlers'''

# Peewee has very poor type hinting support
# pyright: reportUnknownVariableType=false
# pyright: reportMissingTypeArgument=false

import time
from typing import Callable

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.routing import APIRoute

import peewee
from ..exceptions import ItemNotFoundError


class InterceptDbErrorRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                before = time.time()
                response = await original_route_handler(request)
                duration = time.time() - before
                response.headers["X-Response-Time"] = str(duration)
                return response

            # TODO: Add additional db-exceptions as required
            except peewee.DoesNotExist as e:
                raise ItemNotFoundError(str(e))

        return custom_route_handler