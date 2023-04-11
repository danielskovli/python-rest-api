'''API key-entry and related models'''

import datetime

from typing import Any
from .base_model import BaseModel
from enum import Enum, Flag, auto
from functools import total_ordering


@total_ordering
class ApiKeyLevel(Enum):
    '''API key access level.

    Add read-only, write, god modes here as required.

    Do *not* alter existing values, but add whatever you'd like.
    '''

    none = 0
    limited = 100
    read_only = 200
    read_write_limited = 300
    read_write_full = 400
    super_user = 1000

    def __lt__(self, other: 'ApiKeyLevel'):
        if self.__class__ is other.__class__:
            return self.value < other.value

        return NotImplemented


class ApiKeyRoleComparison(Enum):
    '''Defines how to compare roles when querying permissions'''

    any = auto()
    all = auto()


class ApiKeyRole(Flag):
    '''API key roles.

    Bitwise flag/enum that holds all applicable `roles` for a key.

    Construct a list of entitlements/requirements with the bitwise XOR operator (|).

    Do *not* modify the established order of members, but add to the end whatever you'd like.
    '''

    undefined = auto()
    all = auto()
    pizza = auto()
    remote = auto()
    status = auto()


class ApiKeyEntry(BaseModel):
    app_name: str
    key_hash: str
    level = ApiKeyLevel.read_only
    roles = ApiKeyRole.undefined
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

    def has_required_level(self, level: int|ApiKeyLevel):
        value: int = level.value if isinstance(level, Enum) else level
        return self.level.value >= value

    def has_required_roles(self, required_roles: ApiKeyRole, comparison=ApiKeyRoleComparison.any):
        if ApiKeyRole.all in self.roles:
            return True

        if not required_roles:
            return True

        if comparison == ApiKeyRoleComparison.any:
            return any((x in self.roles) for x in required_roles)
        else:
            return all((x in self.roles) for x in required_roles)


class ApiKeys(BaseModel):
    api_keys: list[ApiKeyEntry] = list()


class ApiCredentials(BaseModel):
    api_keys: list[ApiKeyEntry] = list()
    # Future: other creds
