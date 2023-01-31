'''Data model for the `pizza` table'''

# Peewee has very poor type hinting support:
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false

import datetime
import peewee
from ...config import Hosts


# Entities

class BaseModel(peewee.Model):
    class Meta:
        database = Hosts.pizza_sqlite.instance()

class NamedModel(BaseModel):
    '''Contains a `name` property'''

    name = peewee.CharField()


class UniquelyNamedModel(NamedModel):
    '''Contains a unique `name` property'''

    name = peewee.CharField(unique=True)


class Topping(UniquelyNamedModel):
    '''Pizza topping entity'''


class Tag(UniquelyNamedModel):
    '''Tag entity'''


class Pizza(UniquelyNamedModel):
    '''Pizza entity'''

    def toppings(self) -> list['PizzaTopping']:
        return (
            PizzaTopping
            .select()
            .join(Pizza)
            .where(PizzaTopping.pizza == self)
            .order_by(PizzaTopping.topping.name)
        )

    def tags(self) -> list['PizzaTag']:
        return (
            PizzaTag
            .select()
            .join(Pizza)
            .where(PizzaTag.pizza == self)
            .order_by(PizzaTag.tag.name)
        )

    def ratings(self) -> list['PizzaRating']:
        return (
            PizzaRating
            .select()
            .join(Pizza)
            .where(PizzaRating.pizza == self)
            .order_by(PizzaRating.timestamp)
        )


# Relationships

class PizzaRating(BaseModel):
    pizza = peewee.ForeignKeyField(Pizza)
    author = peewee.CharField()
    timestamp = peewee.DateTimeField(default=datetime.datetime.now)
    num_stars = peewee.IntegerField()

class PizzaTopping(BaseModel):
    pizza = peewee.ForeignKeyField(Pizza)
    topping = peewee.ForeignKeyField(Topping)


class PizzaTag(BaseModel):
    pizza = peewee.ForeignKeyField(Pizza)
    tag = peewee.ForeignKeyField(Tag)
