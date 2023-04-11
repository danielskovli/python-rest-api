'''Wikipedia interface'''

from fastapi import APIRouter
from .. import BASE_URL
from .... import utils, security, config


router = APIRouter(
    prefix=BASE_URL + '/remote/random-wiki',
    dependencies=[
        security.qapi_key_dependency(
            required_roles=security.ApiKeyRole.remote
        )
    ]
)


@router.get("/")
async def get_random_article():
    return utils.requests.get_json(
        url=config.RemoteEndpoints.wiki_random
    )