'''Credentials retrieval & storage'''

# FIXME: This most definitely needs to be moved out of source control and into
# the safe, warm, loving embrace of an external keystore
# NOTE: `pseudo_keystore.json` will be overwritten on server by re-deployment

import os
import json
from datetime import datetime

from ..config import Security
from ..exceptions import DuplicateAppNameError, InvalidApiKey
from ..utils import cryptography
from ..models import api_credentials as db_model


class _Cache:
    api_credentials = db_model.ApiCredentials()


class ApiKeys:
    '''API key manager'''

    @classmethod
    def get(
        cls,
        app_name: str,
        key: str,
        only_valid=True
    ) -> db_model.ApiKeyEntry|None:
        '''Retrieve an `ApiKeyEntry` from the database'''

        key_hash = cryptography.hash_api_key(key)
        for entry in _Cache.api_credentials.api_keys:
            if entry.app_name != app_name:
                continue
            elif entry.key_hash != key_hash:
                continue

            elif only_valid and not entry.is_valid():
                continue

            return entry

    @classmethod
    def add(
        cls,
        app_name: str,
        key: str,
        key_level: db_model.ApiKeyLevel|None=None,
        key_expires: datetime|None=None,
        force_lowercase=True
    ) -> dict[str, str]:
        '''Add an API key to the database'''

        if force_lowercase:
            app_name = app_name.lower()

        if app_name in cls._get_all_apps():
            raise DuplicateAppNameError('App with name "{}" has already been registered'.format(app_name))

        if not key or not key.startswith(Security.api_key_prefix) or len(key) < Security.api_key_numbytes:
            raise InvalidApiKey('Proposed API key is empty, invalid or otherwise does not conform to security configuration')

        entry = db_model.ApiKeyEntry(
            app_name=app_name,
            key_hash=cryptography.hash_api_key(key)
        )

        if key_level is not None:
            entry.level = key_level

        if key_expires is not None:
            entry.expires_utc = key_expires

        _Cache.api_credentials.api_keys.append(entry)
        _save_json()

        return {
            'app-name': app_name,
            'api-key': key
        }

    @classmethod
    def remove(cls, app_name: str) -> bool:
        '''Remove an `ApiKeyEntry` from the database'''

        for i, _ in cls._enumerate(target_app=app_name):
            _Cache.api_credentials.api_keys.pop(i)
            return True # Assume single match only

        return False

    @classmethod
    def disable(cls, app_name: str) -> bool:
        '''Disable an `ApiKeyEntry` in the database'''

        for _, entry in cls._enumerate(target_app=app_name):
            entry.enabled = False
            return True # Assume single match only

        return False

    @classmethod
    def enable(cls, app_name: str) -> bool:
        '''Enable an `ApiKeyEntry` in the database'''

        for _, entry in cls._enumerate(target_app=app_name):
            entry.enabled = True
            return True # Assume single match only

        return False

    @classmethod
    def _get_all_apps(cls) -> list[str]:
        '''Internal: Retrieve all registered app names'''

        return [x.app_name for x in _Cache.api_credentials.api_keys]

    @classmethod
    def _enumerate(cls, target_app: str|None = None):
        '''Internal: Enumerate over the `ApiKeyEntry` records in the database,
        optionally filtering by `target_app` name
        '''

        for x in enumerate(_Cache.api_credentials.api_keys):
            if target_app is not None and x[1].app_name != target_app:
                continue

            yield x


def _get_json_path() -> str:
    json_path = os.path.splitext(__file__)[0]
    return '{}.json'.format(json_path)


def _load_json() -> None:
    json_path = _get_json_path()

    if not os.path.isfile(json_path):
        _Cache.api_credentials = db_model.ApiCredentials()

    with open(json_path, 'r') as f:

        try:
            _Cache.api_credentials = db_model.ApiCredentials.parse_obj(
                json.load(f)
            )
        except Exception as e:
            print('Error loading JSON from file: {}'.format(e))
            _Cache.api_credentials = db_model.ApiCredentials()


def _save_json():
    json_path = _get_json_path()
    with open(json_path, 'w') as f:
        f.write(_Cache.api_credentials.json(indent=4))


# Init
_load_json()