from typing import Any
from pydantic import Field


HIDDEN_TAG = 'hidden'
SENSITIVE_TAG = 'sensitive_data'
ALL_HIDE_TAGS = [
    HIDDEN_TAG,
    SENSITIVE_TAG
]


def SensitiveDataField(*args: Any, **kwargs: Any):
    for tag in ALL_HIDE_TAGS:
        kwargs.setdefault(tag, True)

    return Field(*args, **kwargs)