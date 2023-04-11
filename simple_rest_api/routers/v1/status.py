'''Hypothetical server/whatever status endpoint'''

from . import BASE_URL
from ... import security, uptime, __version__
from fastapi import APIRouter, Request


router = APIRouter(
    prefix=BASE_URL + '/status',
    dependencies=[
        security.qapi_key_dependency(
            required_roles=security.ApiKeyRole.status
        )
    ]
)


@router.get("/")
async def status(request: Request):
    return {
        'status': 'a-okay',
        'caller': request.client.host if request.client else 'unknown',
        'server-version': __version__,
        'server-uptime': uptime()
    }