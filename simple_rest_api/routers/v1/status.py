'''Hypothetical server/whatever status endpoint'''

from . import BASE_URL
from fastapi import APIRouter, Request


router = APIRouter(
    prefix=BASE_URL + '/status'
)


@router.get("/")
async def status(request: Request):
    return {
        'status': 'a-okay',
        'caller': request.client.host if request.client else 'unknown'
    }