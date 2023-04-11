'''Request timing'''

from typing import Callable, Coroutine, Any
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from fastapi import Request, Response
from fastapi.routing import APIRoute

import peewee
from ..exceptions import ItemNotFoundError


class InterceptDbErrorMiddleware(BaseHTTPMiddleware):
    '''Intercept common DB exceptions and offer a nicer JSON return structure for the caller'''

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        return await database_runner(request, call_next)


class InterceptDbErrorRoute(APIRoute):
    '''Intercept common DB exceptions and offer a nicer JSON return structure for the caller'''

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            return await database_runner(request, original_route_handler)

        return custom_route_handler


async def database_runner(request: Request, runner: RequestResponseEndpoint):
    '''Common runner-hook for middleware/routes wanting to catch peewee errors'''

    try:
        return await runner(request)

    # TODO: Add additional db-exceptions as required
    except peewee.DoesNotExist as e:
        raise ItemNotFoundError(str(e))
