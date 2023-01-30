'''Constant values.

Things we need a record of, but shouldn't really be changed willy nilly
'''

from enum import Enum


HIDDEN_TAG = 'hidden'
SENSITIVE_TAG = 'sensitive_data'
ALL_HIDE_TAGS = [
    HIDDEN_TAG,
    SENSITIVE_TAG
]


class HashingMethod(str, Enum):
    md5 = 'md5'
    sha256 = 'sha256'
    sha512 = 'sha512'