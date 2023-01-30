'''Custom pydantic fields'''

from typing import Any
from pydantic import Field

from .constants import ALL_HIDE_TAGS


def SensitiveDataField(*args: Any, **kwargs: Any):
    '''Defines a `pydantic.Field` tagged as containing sensitive data'''

    for tag in ALL_HIDE_TAGS:
        kwargs.setdefault(tag, True)

    return Field(*args, **kwargs)