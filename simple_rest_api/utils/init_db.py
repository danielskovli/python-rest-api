'''Demo-db initialization and data population'''

# pyright: reportUnknownMemberType=false

import random
import pydantic

from ..config import Hosts
from ..models.sql import pizza as schema
from ..crud import pizza as db


def create_tables():
    Hosts.pizza_sqlite.instance().create_tables([
        schema.Topping,
        schema.Tag,
        schema.Pizza,
        schema.PizzaRating,
        schema.PizzaTopping,
        schema.PizzaTag
    ])


def populate_demo_data():
    class _DemoPizza(pydantic.BaseModel):
        name: str
        toppings: list[str]
        tags: list[str] = []

    pizzas = [
        _DemoPizza(
            name='Margherita',
            toppings=['Mozarella', 'Basil'],
            tags=['classic', 'simple']
        ),
        _DemoPizza(
            name='Pepperoni',
            toppings=['Mozarella', 'Pepperoni'],
            tags=['family favorite']
        ),
        _DemoPizza(
            name='Veggie Supreme',
            toppings=['Mozarella', 'Onions', 'Mushrooms', 'Olives', 'Basil']
        )
    ]

    for pizza in pizzas:
        entity = db.create(schema.Pizza, pizza.name)
        [db.add_topping(entity, x) for x in pizza.toppings]
        [db.add_tag(entity, x) for x in pizza.tags]
        db.rate(entity, 'anonymous', random.randint(3, 5))
