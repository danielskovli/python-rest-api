'''Wikipedia interface'''

from fastapi import APIRouter

from .. import BASE_URL
from ....utils import requests
from ....config import RemoteEndpoints
from ....middleware.route_handlers import RequestTimingRoute


router = APIRouter(
    prefix=BASE_URL + '/remote/random-wiki',
    route_class=RequestTimingRoute
)


@router.get("/")
async def get_random_article():
    return requests.get_json(
        url=RemoteEndpoints.wiki_random
    )