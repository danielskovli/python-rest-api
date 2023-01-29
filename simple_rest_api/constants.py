'''Constant values.

Things we need a record of, but shouldn't really be changed willy nilly
'''

from enum import Enum


class HashingMethod(str, Enum):
    md5 = 'md5'
    sha256 = 'sha256'
    sha512 = 'sha512'