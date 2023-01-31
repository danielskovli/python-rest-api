'''Request utilities'''

from typing import Any

import json
import requests


class _OmittedArg:
    pass
_OMITTED_ARG = _OmittedArg()


def get_json(url: str, fallback_plaintext: bool=False, user_agent: str|_OmittedArg|None=_OMITTED_ARG) -> dict[str, Any]|str:
    '''Convenience method for making a `get` request and parsing the output as `json`'''

    if not isinstance(user_agent, _OmittedArg):
        headers = {
            "User-Agent": user_agent
        }
    else:
        headers = None

    r = requests.get(
        url=url,
        headers=headers # type: ignore
    )

    try:
        return json.loads(r.text)
    except Exception:
        if fallback_plaintext:
            return r.text

        raise