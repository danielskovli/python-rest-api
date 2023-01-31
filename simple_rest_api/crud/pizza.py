'''CRUD operations for the pizza table'''

# Peewee has very poor type hinting support:
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false

from typing import Type, TypeVar
from contextlib import contextmanager
import peewee

from ..config import Hosts
from ..models.sql.pizza import (
    BaseModel,
    NamedModel,
    Tag,
    Topping,
    Pizza,
    PizzaRating,
    PizzaTag,
    PizzaTopping
)


T = TypeVar('T', bound=NamedModel)

@contextmanager
def atomic_write():
    with Hosts.pizza_sqlite.instance().atomic() as transaction:
        try:
            yield
        except Exception:
            transaction.rollback()
            raise


def _entity_query(query: T|str|int, model: Type[T], create_=False) -> T:
    '''Convenience method: Retrieve an entity by either:
        1) Passthrough (you already had an instance)
        2) Name (unique)
        3) Id (primary key)

    Args:
        query (NamedModel|str|int): Either passthrough `NamedModel` entity or name|id to look up
        model (NamedModel): Database model to use for lookup
        create_ (bool, optional): Specify True to create entity if required and
            if querying by `name`. Defaults to False

    Raises:
        DoesNotExist: No entities were found by the given query arguments

    Returns:
        NamedModel: The entity matching the query
    '''

    if isinstance(query, int):
        return get(model, id=query)
    elif isinstance(query, str):
        return get(model, name=query, create_=create_)
    else:
        return query


def get(model: Type[T], id: int|None=None, name: str|None=None, create_=False, case_sensitive=False) -> T:
    '''Retrieve a single entity from the database, either by `name` or `id`

    Args:
        model (NamedModel): Database model to use for lookup
        id (int|None, optional): Entity ID. Defaults to None
        name (str|None, optional): Entity name. Defaults to None
        create_ (bool, optional): Specify True to create entity if required and
            if querying by `name`. Defaults to False
        case_sensitive (bool, optional): Should the `name` query for existing records be case sensitive?
            Defaults to False

    Raises:
        ValueError: Both `id` and `name` arguments omitted
        DoesNotExist: No entities of type `T` found by the given `id` or `name`

    Returns:
        NamedModel: The entity matching the query
    '''

    if id is not None:
        return model.get_by_id(id)
    elif name is not None:
        if create_:
            return create(model, name=name, case_sensitive=False)
        elif case_sensitive:
            return model.get(name=name)
        else:
            return model.get(model.name ** name)
    else:
        raise ValueError('Must have either `id` or `name` for lookup, neither was supplied')


def create(model: Type[T], name: str, case_sensitive=False, allow_existing=True) -> T:
    '''Create a model with the given `name`.
    
    If such an entity already exists, return it instead.

    Args:
        model (NamedModel): Database model to use for lookup and/or insert
        name (str): Entity name
        case_sensitive (bool, optional): Should the `name` query for existing records be case sensitive?
            Defaults to False
        allow_existing (bool, optional): Allow existing entries? If False, this method MUST create an entity.
            If True, this method will act as `get_or_create`. Defaults to True

    Returns:
        NamedModel: The entity matching the query or a freshly created one
    '''

    # return model.get_or_create(name=name)[0] <- can't handle a query, only straight up kw matching

    entity = None
    if case_sensitive:
        entity = model.get_or_none(name=name)
    else:
        entity = model.get_or_none(model.name ** name)

    if entity:
        if not allow_existing:
            raise peewee.DataError('Entity with name `{}` already exists'.format(name))

        return entity
    else:
        with atomic_write():
            return model.create(name=name)


def rename(model: Type[T], id: int, new_name: str) -> T:
    entity = get(model, id)
    with atomic_write():
        entity.name = new_name # type: ignore
        entity.save()
        return entity


def delete(model: Type[BaseModel], id: int, recursive=True) -> int:
    entity = model.get_by_id(id)
    return entity.delete_instance(recursive=recursive)


def rate(pizza: Pizza|str|int, author: str, num_stars: int) -> PizzaRating:
    if num_stars < 0 or num_stars > 5:
        raise ValueError('Number of stars given must be a value between 0 and 5 (inclusive')

    return PizzaRating.create(
        pizza=_entity_query(pizza, Pizza),
        author=author,
        num_stars=num_stars
    )


def add_tag(pizza: Pizza|int|str, tag: Tag|int|str) -> PizzaTag:
    return PizzaTag.create(
        pizza=_entity_query(pizza, Pizza),
        tag=_entity_query(tag, Tag, create_=True)
    )


def remove_tag(pizza: Pizza|str|int, tag: Tag|int|str) -> int:
    pizza = _entity_query(pizza, Pizza)
    tag = _entity_query(tag, Tag)

    with atomic_write():
        return (
            PizzaTag
            .delete()
            .where(
                PizzaTag.pizza == pizza,
                PizzaTag.tag == tag
            )
            .execute()
        )


def delete_tag(tag: Tag|int|str):
    with atomic_write():
        tag_entity = _entity_query(tag, Tag)
        tag_entity.delete_instance(recursive=True)


def add_topping(pizza: Pizza|int|str, topping: Topping|int|str) -> PizzaTopping:
    return PizzaTopping.create(
        pizza=_entity_query(pizza, Pizza),
        topping=_entity_query(topping, Topping, create_=True)
    )


def remove_topping(pizza: Pizza|str|int, topping: Topping|int|str) -> int:
    pizza = _entity_query(pizza, Pizza)
    topping = _entity_query(topping, Topping)

    with atomic_write():
        return (
            PizzaTopping
            .delete()
            .where(
                PizzaTopping.pizza == pizza,
                PizzaTopping.topping == topping
            )
            .execute()
        )


def delete_topping(topping: Topping|int|str):
    with atomic_write():
        tag_entity = _entity_query(topping, Topping)
        tag_entity.delete_instance(recursive=True)


def create_complete_pizza(name: str, toppings: list[str], tags: list[str]|None=None):
    entity = create(Pizza, name, allow_existing=False)
    [add_topping(entity, x) for x in toppings]

    if tags:
        [add_tag(entity, x) for x in tags]

    return entity