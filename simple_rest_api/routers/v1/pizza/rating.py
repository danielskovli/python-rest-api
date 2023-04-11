'''Pizza ratings'''

# Peewee has very poor type hinting support
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportMissingTypeStubs=false

from fastapi import APIRouter
from playhouse.shortcuts import model_to_dict

from .. import BASE_URL
from ....middleware.errors import InterceptDbErrorRoute
from ....models.payloads.v1 import pizza as payloads
from ....models.sql import pizza as schema
from ....crud import pizza as db
from .... import security


CAN_ADD_RATING = [security.qapi_key_dependency(required_level=security.ApiKeyLevel.read_write_limited)]
CAN_DELETE_RATING = [security.qapi_key_dependency(required_level=security.ApiKeyLevel.read_write_full)]


router = APIRouter(
    prefix=BASE_URL + '/pizza/rating',
    route_class=InterceptDbErrorRoute,
    dependencies=[
        security.qapi_key_dependency(
            required_roles=security.ApiKeyRole.pizza
        )
    ]
)


@router.get("/")
async def get_all():
    '''Get all ratings'''

    return [
        model_to_dict(x) for x in schema.PizzaRating.select()
    ]


@router.get("/{id}")
async def get_one(id: int):
    '''Get specific rating'''

    entity = schema.PizzaRating.get_by_id(id)
    return model_to_dict(entity)


@router.post("/", dependencies=CAN_ADD_RATING)
async def create_one(payload: payloads.Rating):
    '''Create a new rating'''

    entity = db.rate(
        pizza=payload.pizza_id,
        author=payload.author,
        num_stars=payload.num_stars
    )

    return model_to_dict(entity)


@router.delete("/{id}", dependencies=CAN_DELETE_RATING)
async def delete_one(id: int):
    '''Delete specific rating'''

    return {
        'affected-rows': db.delete(schema.PizzaRating, id=id, recursive=False)
    }