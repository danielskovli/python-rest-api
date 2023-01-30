'''CRUD operations for the pizza table'''

# pyright: reportUnknownParameterType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false

from typing import Type, TypeVar
from contextlib import contextmanager

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
def _atomic_write():
    with Hosts.pizza_sqlite.instance().atomic() as transaction:
        try:
            yield
        except Exception:
            transaction.rollback()
            raise


def _entity_query(query: T|str|int, model: Type[T], create=False) -> T:
    '''Convenience method: Retrieve an entity by either:
        1) Passthrough (you already had an instance)
        2) Name (unique)
        3) Id (primary key)

    Args:
        query (NamedModel|str|int): Either passthrough `NamedModel` entity or name|id to look up
        model (NamedModel): Database model to use for lookup
        create (bool, optional): Specify True to create entity if required and
            if querying by `name`. Defaults to False

    Returns:
        NamedModel: The entity matching the query
    '''

    if isinstance(query, int):
        return get(model, id=query)
    elif isinstance(query, str):
        return get(model, name=query, create=create)
    else:
        return query


def get(model: Type[T], id: int|None=None, name: str|None=None, create=False) -> T:
    '''Retrieve a single entity from the database, either by `name` or `id`

    Args:
        model (NamedModel): Database model to use for lookup
        id (int|None, optional): Entity ID. Defaults to None
        name (str|None, optional): Entity name. Defaults to None
        create (bool, optional): Specify True to create entity if required and
            if querying by `name`. Defaults to False

    Raises:
        ValueError: Both `id` and `name` arguments omitted
        DoesNotExist: No entities of type `T` found by the given `id` or `name`

    Returns:
        NamedModel: The entity matching the query
    '''

    if id is not None:
        return model.get_by_id(id)
    elif name is not None:
        if create:
            return model.get_or_create(name=name)[0]
        else:
            return model.get(name=name)
    else:
        raise ValueError('Must have either `id` or `name` for lookup, neither was supplied')


def create(model: Type[T], name: str) -> T:
    return model.get_or_create(name=name)[0]


def rename(model: Type[T], id: int, new_name: str) -> T:
    entity = get(model, id)
    with _atomic_write():
        entity.name = new_name # type: ignore
        entity.save()
        return entity


def delete(model: Type[BaseModel], id: int):
    model.delete_by_id(id)


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
        tag=_entity_query(tag, Tag, create=True)
    )


def remove_tag(pizza: Pizza|str|int, tag: Tag|int|str) -> int:
    pizza = _entity_query(pizza, Pizza)
    tag = _entity_query(tag, Tag)

    with _atomic_write():
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
    with _atomic_write():
        tag_entity = _entity_query(tag, Tag)
        tag_entity.delete_instance(recursive=True)


def add_topping(pizza: Pizza|int|str, topping: Topping|int|str) -> PizzaTopping:
    return PizzaTopping.create(
        pizza=_entity_query(pizza, Pizza),
        topping=_entity_query(topping, Topping, create=True)
    )


def remove_topping(pizza: Pizza|str|int, topping: Topping|int|str) -> int:
    pizza = _entity_query(pizza, Pizza)
    topping = _entity_query(topping, Topping)

    with _atomic_write():
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
    with _atomic_write():
        tag_entity = _entity_query(topping, Topping)
        tag_entity.delete_instance(recursive=True)
