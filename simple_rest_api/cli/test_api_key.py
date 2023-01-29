import sys
import argparse

from simple_rest_api import tempstorage
from pydantic import BaseModel


class Args(BaseModel):
    app_name: str
    api_key: str


def main():
    args = parse_args()
    print(f'Args passed validation: {args}')

    result = tempstorage.pseudo_keystore.ApiKeys.get(
        app_name=args.app_name,
        key=args.api_key
    )

    if result is None:
        print('Supplied app name and/or API key were invalid')
        return

    print('API key from database was:')
    print(result)


def parse_args() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument('app_name')
    parser.add_argument('api_key')

    args = sys.argv[1:]
    parsed = parser.parse_args(args=args)
    args = Args(
        # Removing potential argument-name from the payload, if user supplied app_name=<name>
        app_name=parsed.app_name.strip().replace('app_name=', ''),
        api_key=parsed.api_key.strip().replace('api_key=', '')
    )

    # Simple validation
    assert bool(args.app_name), 'Missing or empty argument app_name'
    assert bool(args.api_key), 'Missing or empty argument api_key'

    return args


if __name__ == '__main__':
    main()