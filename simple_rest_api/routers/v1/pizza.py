'''it'za-pizza-pie'''

# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportMissingTypeStubs=false

from typing import Any
from fastapi import APIRouter
from playhouse.shortcuts import model_to_dict

from . import BASE_URL
from ...models.sql.pizza import Pizza


router = APIRouter(
    prefix=BASE_URL + '/pizza'
)


@router.get("/all")
async def root():
    pizzas: list[dict[str, Any]] = []

    entity: Pizza
    for entity in Pizza.select():
        x = model_to_dict(entity)
        x['toppings'] = [model_to_dict(z.topping) for z in entity.toppings()]
        x['tags'] = [model_to_dict(z.tag) for z in entity.tags()]
        x['ratings'] = [model_to_dict(z) for z in entity.ratings()]

        # Small cleanup job since I can't get peewee to drop fk output here
        for _ in x['ratings']:
            _.pop('pizza')

        pizzas.append(x)

    return pizzas
