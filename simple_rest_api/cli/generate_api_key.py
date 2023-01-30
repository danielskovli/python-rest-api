'''Generate API keys'''

import sys
import argparse

from pydantic import BaseModel
from simple_rest_api import utils, tempstorage


class Args(BaseModel):
    app_name: str


def main():
    args = parse_args()
    print(f'Args passed validation: {args}')

    result = tempstorage.pseudo_keystore.ApiKeys.add(
        app_name=args.app_name,
        key=utils.cryptography.generate_api_key()
    )

    print('API key successfully created')
    print('Store this information carefully, it cannot be retrieved later:')
    print(result)


def parse_args() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument('app_name')

    args = sys.argv[1:]
    parsed = parser.parse_args(args=args)
    args = Args(
        # Removing potential argument-name from the payload, if user supplied app_name=<name>
        app_name=parsed.app_name.strip().replace('app_name=', '')
    )

    # Simple validation
    assert bool(args.app_name), 'Missing or empty argument app_name'

    return args


if __name__ == '__main__':
    main()