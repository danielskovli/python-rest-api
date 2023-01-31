'''Demo-db initialization and data population'''

# Peewee has very poor type hinting support
# pyright: reportUnknownMemberType=false

import random
import pydantic

from ..config import Hosts
from ..models.sql import pizza as schema
from ..models.payloads.v1 import pizza as payloads
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
    pizzas = [
        payloads.Pizza(
            name='Margherita',
            toppings=['Mozarella', 'Basil'],
            tags=['classic', 'simple']
        ),
        payloads.Pizza(
            name='Pepperoni',
            toppings=['Mozarella', 'Pepperoni'],
            tags=['family favorite']
        ),
        payloads.Pizza(
            name='Veggie Supreme',
            toppings=['Mozarella', 'Onions', 'Mushrooms', 'Olives', 'Basil']
        )
    ]

    for pizza in pizzas:
        entity = db.create_complete_pizza(
            name=pizza.name,
            toppings=pizza.toppings,
            tags=pizza.tags
        )
        db.rate(entity, 'anonymous', random.randint(3, 5))
