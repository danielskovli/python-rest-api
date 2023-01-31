from typing import Any

import json
import requests


class _OMITTED_ARG:
    pass


def get_json(url: str, fallback_plaintext: bool=False, user_agent: str|_OMITTED_ARG|None=_OMITTED_ARG()) -> dict[str, Any]|str:
    if not isinstance(user_agent, _OMITTED_ARG):
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