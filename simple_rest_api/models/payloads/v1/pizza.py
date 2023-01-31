'''Data model for the /pizza router'''

from pydantic import Field
from ...base_model import BaseModel


class NamedModel(BaseModel):
    name: str


class Pizza(NamedModel):
    toppings: list[str]
    tags: list[str] = []


class Rating(BaseModel):
    pizza_id: int
    author: str
    num_stars: int = Field(gt=-1, lt=6)