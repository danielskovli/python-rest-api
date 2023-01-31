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
from ....middleware.route_handlers import InterceptDbErrorRoute
from ....models.payloads.v1 import pizza as payloads
from ....models.sql import pizza as schema
from ....crud import pizza as db


router = APIRouter(
    prefix=BASE_URL + '/pizza/rating',
    route_class=InterceptDbErrorRoute
)


@router.get("/")
async def get_all():
    '''Get all ratings'''

    return [
        model_to_dict(x) for x in schema.PizzaRating.select()
    ]


@router.post("/")
async def create_one(payload: payloads.Rating):
    '''Create a new rating'''

    entity = db.rate(
        pizza=payload.pizza_id,
        author=payload.author,
        num_stars=payload.num_stars
    )

    return model_to_dict(entity)


@router.get("/{id}")
async def get_one(id: int):
    '''Get specific rating'''

    entity = schema.PizzaRating.get_by_id(id)
    return model_to_dict(entity)


@router.delete("/{id}")
async def delete_one(id: int):
    '''Delete specific rating'''

    return {
        'affected-rows': db.delete(schema.PizzaRating, id=id, recursive=False)
    }