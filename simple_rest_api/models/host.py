'''Host models'''

import uuid
from typing import Any

import peewee
from pydantic import Field
from .base_model import BaseModel
from ..fields import SensitiveDataField


class Host(BaseModel):
    hostname: str|None = None
    port: int|None = None
    protocol: str|None = None
    id: str = Field(
        default_factory=lambda: f'{uuid.uuid4()}'
    )


class DatabaseHost(Host):
    database: str


class InMemorySqliteHost(DatabaseHost):
    database: str = ':memory:'

    # Reasonable defaults, as per peewee docs
    pragmas: dict[str, Any] = {
        'journal_mode': 'wal',
        'cache_size': -1 * 64000, # 64MB
        'foreign_keys': 1,
        'ignore_check_constraints': 0,
        'synchronous': 0
    }

    xyz_instance_: peewee.SqliteDatabase|None = None

    class Config:
        arbitrary_types_allowed = True

    def instance(self):
        if not self.xyz_instance_:
            self.xyz_instance_ = peewee.SqliteDatabase(
                self.database,
                pragmas=self.pragmas
            )

        return self.xyz_instance_


# Future: SQL Alchemy scaffolding
class MysqlHost(DatabaseHost):
    port: int = 3306
    protocol: str = 'mysql+aiomysql'


class DbConfig(BaseModel):
    host: DatabaseHost
    username: str
    password: str = SensitiveDataField()

    @property
    def url(self) -> str:
        return f'{self.host.protocol}://{self.username}:{self.password}@{self.host.hostname}/{self.host.database}'