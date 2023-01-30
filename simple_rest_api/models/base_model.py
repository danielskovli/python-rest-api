'''simple-rest-api specific version of the pydantic.BaseModel'''

from typing import Any
from pydantic import BaseModel as _BaseModel
from ..constants import ALL_HIDE_TAGS


class BaseModel(_BaseModel):
    def dict(self, **kwargs: Any):
        hidden_fields = set(
            attribute_name
            for attribute_name, model_field in self.__fields__.items()
            if any(model_field.field_info.extra.get(x) for x in ALL_HIDE_TAGS)
        )
        if 'exclude' in kwargs and kwargs['exclude'] is not None:
            if isinstance(kwargs['exclude'], set):
                kwargs['exclude'].update(hidden_fields) # type: ignore
            else:
                kwargs['exclude'].update({x: True for x in hidden_fields})
        else:
            kwargs["exclude"] = hidden_fields or None

        return super().dict(**kwargs)