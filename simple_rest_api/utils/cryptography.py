'''Cryptography utilities'''

import secrets
import hashlib
from ..config import Security

# NOTE: Realistically these methods require some form of versioning
# It is incredibly unlikely that the creation and/or usage of API keys
# will remain unchanged throughout the life cycle of an application


def generate_api_key(prefix: str|None=None, length: int|None=None) -> str:
    '''Generates an API key with desired length, as per `config.Security.api_key_length`

    Args:
        prefix (str, optional): Key prefix. Empty string allowed (no prefix). Defaults to `config.Security.api_key_prefix`
        length (int, optional): Key length (exclusive of `prefix`). Must be a postive integer. Defaults to `config.Security.api_key_length`

    Returns:
        str: The generated key
    '''

    if prefix is None:
        prefix = Security.api_key_prefix

    if length is None or length < 1:
        length = Security.api_key_numbytes - len(prefix)

    key = secrets.token_urlsafe(length)
    return '{}{}'.format(
        prefix,
        key
    )


def hash_api_key(key: str, method: str|None=None) -> str:
    '''Hash an api key for storage and comparison
    
    Args:
        key (str): The key to hash
        method (str, optional): The hashing method to use. Defaults to `config.Security.Hashing.api_key_method`

    Return:
        str: The hashed result (hexdigest)
    '''

    hasher = hashlib.new(method or Security.Hashing.api_key_method)
    hasher.update(key.encode('utf-8'))

    return hasher.hexdigest()