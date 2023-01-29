import datetime

from typing import Any
from .base_model import BaseModel
from enum import Enum
from functools import total_ordering


@total_ordering
class ApiKeyLevel(Enum):
    default = 10

    def __lt__(self, other: Any):
        if self.__class__ is other.__class__:
            return self.value < other.value

        return NotImplemented


class ApiKeyEntry(BaseModel):
    app_name: str
    key_hash: str
    level = ApiKeyLevel.default
    enabled = True
    created_utc = datetime.datetime.now(tz=datetime.timezone.utc)
    expires_utc = datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)

    def is_valid(self, level:ApiKeyLevel|None = None) -> bool:
        if not self.enabled:
            return False

        if level is not None and self.level < level:
            return False

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        if self.expires_utc <= now:
            return False

        return True


class ApiKeys(BaseModel):
    api_keys: list[ApiKeyEntry] = list()


class ApiCredentials(BaseModel):
    api_keys: list[ApiKeyEntry] = list()
    # Future: other creds
