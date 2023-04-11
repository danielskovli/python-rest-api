'''Itsa-Pizza-Pie'''

# Peewee has very poor type hinting support:
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportMissingTypeStubs=false

from typing import Any
from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError
from pydantic.error_wrappers import ErrorWrapper
from playhouse.shortcuts import model_to_dict

from .. import BASE_URL
from ....middleware.errors import InterceptDbErrorRoute
from ....models.payloads.v1 import pizza as payloads
from ....models.sql import pizza as schema
from ....crud import pizza as db
from .... import security


CAN_ADD_PIZZA = [security.qapi_key_dependency(required_level=security.ApiKeyLevel.read_write_limited)]
CAN_DELETE_PIZZA = [security.qapi_key_dependency(required_level=security.ApiKeyLevel.read_write_full)]


router = APIRouter(
    prefix=BASE_URL + '/pizza',
    route_class=InterceptDbErrorRoute,
    dependencies=[
        security.qapi_key_dependency(
            required_roles=security.ApiKeyRole.pizza
        )
    ]
)


def _serialize_pizza_entity(entity: schema.Pizza) -> dict[str, Any]:
    '''Helper: Include all known traits and serialize a given `Pizza` entity'''

    x = model_to_dict(entity)
    x['toppings'] = [model_to_dict(z.topping) for z in entity.toppings()]
    x['tags'] = [model_to_dict(z.tag) for z in entity.tags()]
    x['ratings'] = [model_to_dict(z) for z in entity.ratings()]

    # Small cleanup job since I can't get peewee to drop fk output here
    for _ in x['ratings']:
        _.pop('pizza')

    return x


@router.get("/")
async def get_all():
    '''Get all pizzas'''

    pizzas: list[dict[str, Any]] = []

    entity: schema.Pizza
    for entity in schema.Pizza.select():
        pizzas.append(_serialize_pizza_entity(entity)) # pyright: reportUnknownArgumentType=false

    return pizzas


@router.get("/{id}")
async def get_one(id: int):
    '''Get specific pizza'''

    return _serialize_pizza_entity(db.get(schema.Pizza, id=id))


@router.get("/find")
@router.post("/find")
async def find_one(name: str|None=None, payload: payloads.NamedModel|None=None):
    '''Search for a pizza by name'''

    # TODO: This should become a piece of middleware, surely
    if payload:
        loc = ('body',)
        name = payload.name
    else:
        loc = ('query', 'name')

    if not name:
        raise RequestValidationError([
            ErrorWrapper(
                ValueError('field required'),
                loc
            )
        ])

    return _serialize_pizza_entity(db.get(schema.Pizza, name=name))


@router.post("/", dependencies=CAN_ADD_PIZZA)
async def create_one(payload: payloads.Pizza):
    '''Create a new pizza'''

    entity = db.create_complete_pizza(
        name=payload.name,
        toppings=payload.toppings,
        tags=payload.tags
    )

    return _serialize_pizza_entity(entity)


@router.delete("/{id}", dependencies=CAN_DELETE_PIZZA)
async def delete_one(id: int):
    '''Delete specific pizza'''

    return {
        'affected-rows': db.delete(schema.Pizza, id=id)
    }


@router.put("/{id}", dependencies=CAN_ADD_PIZZA)
async def update_one(id: int, payload: payloads.Pizza):
    '''Update specific pizza'''

    with db.atomic_write():
        entity = db.rename(schema.Pizza, id, payload.name)

        schema.PizzaTopping.delete().where(schema.PizzaTopping.pizza == entity).execute()
        for topping in payload.toppings:
            db.add_topping(entity, topping)

        schema.PizzaTag.delete().where(schema.PizzaTag.pizza == entity).execute()
        for tag in payload.tags:
            db.add_tag(entity, tag)

        return _serialize_pizza_entity(entity)
