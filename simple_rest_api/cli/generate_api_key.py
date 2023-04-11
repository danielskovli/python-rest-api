'''Generate API keys'''

import sys
import argparse

from operator import or_
from functools import reduce
from typing import Optional
from pydantic import BaseModel
from simple_rest_api import utils, tempstorage
from simple_rest_api.models.api_credentials import ApiKeyRole, ApiKeyLevel


class Args(BaseModel):
    app_name: str
    key_roles: Optional[str]=None
    key_level: Optional[str]=None


def main():
    args = parse_args()

    key_level: ApiKeyLevel|None = None
    if args.key_level:
        try:
            key_level = ApiKeyLevel.__members__[args.key_level]
        except KeyError:
            key_level = ApiKeyLevel(int(args.key_level))

    key_roles: ApiKeyRole|None = None
    if args.key_roles:
        try:
            flags: list[ApiKeyRole] = []
            for role in args.key_roles.split(','):
                _role = role.strip()
                flags.append(ApiKeyRole.__members__[_role])

            key_roles = reduce(or_, flags)
        except KeyError as e:
            raise ValueError(f'Invalid key role `{e.args[0]}`')

    result = tempstorage.pseudo_keystore.ApiKeys.add(
        app_name=args.app_name,
        key=utils.cryptography.generate_api_key(),
        key_level=key_level,
        key_roles=key_roles
    )

    print('API key successfully created')
    print('Store this information carefully, it cannot be retrieved manually:')
    print(result)


def parse_args() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument('app_name')
    parser.add_argument('key_roles')
    parser.add_argument('key_level')

    parsed = parser.parse_args(args=sys.argv[1:])
    args = Args(
        # Removing potential argument-names from the payload
        app_name=parsed.app_name.strip().replace('app_name=', ''),
        key_roles=parsed.key_roles.strip().replace('key_roles=', ''),
        key_level=parsed.key_level.strip().replace('key_level=', '')
    )

    # Simple validation
    assert bool(args.app_name), 'Missing or empty argument app_name'
    assert ' ' not in args.app_name, 'Spaces are not allowed in app_name'

    return args


if __name__ == '__main__':
    main()