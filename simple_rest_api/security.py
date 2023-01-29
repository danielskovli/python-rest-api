'''Security scheme definitions'''

from typing import Optional, Any

from fastapi import HTTPException, Request, status, Security
from fastapi.security import APIKeyHeader, APIKeyQuery

from . import config
from .tempstorage import pseudo_keystore
from .models.api_credentials import ApiKeyEntry


class ApiKeyAuthScheme:
    query_key_scheme_name = 'ApiKeyQuery'
    query_app_scheme_name = 'AppNameQuery'
    header_key_scheme_name = 'ApiKeyHeader'
    header_app_scheme_name = 'AppNameHeader'

    api_key_query = APIKeyQuery(name=config.Security.Query.api_key, auto_error=False, scheme_name=query_key_scheme_name)
    app_name_query = APIKeyQuery(name=config.Security.Query.app_name, auto_error=False, scheme_name=query_app_scheme_name)
    api_key_header = APIKeyHeader(name=config.Security.Headers.api_key, auto_error=False, scheme_name=header_key_scheme_name)
    app_name_header = APIKeyHeader(name=config.Security.Headers.app_name, auto_error=False, scheme_name=header_app_scheme_name)

    async def __call__(self,
        request: Request,
        api_key_query: str = Security(api_key_query),
        app_name_query: str = Security(app_name_query),
        api_key_header: str = Security(api_key_header),
        app_name_header: str = Security(app_name_header)
    ) -> Optional[ApiKeyEntry]:
        request.state.api_key = None

        if api_key_header and app_name_header:
            request.state.api_key = pseudo_keystore.ApiKeys.get(
                app_name=app_name_header,
                key=api_key_header
            )
        elif api_key_query and app_name_query:
            request.state.api_key = pseudo_keystore.ApiKeys.get(
                app_name=app_name_query,
                key=api_key_query
            )

        if request.state.api_key is None or not request.state.api_key.is_valid():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized"
            )

        return request.state.api_key


def merge_securities(securities: list[dict[str, list[Any]]]) -> list[dict[Any, Any]]:
    '''Find our pairs of securities and merge them'''

    original_securities: list[Any] = []
    custom_securities: list[Any] = []
    custom_security_header: dict[Any, Any] = {}
    custom_security_query: dict[Any, Any] = {}

    for security in securities:
        if ApiKeyAuthScheme.header_key_scheme_name in security or ApiKeyAuthScheme.header_app_scheme_name in security:
            custom_security_header.update(security)
        elif ApiKeyAuthScheme.query_key_scheme_name in security or ApiKeyAuthScheme.query_app_scheme_name in security:
            custom_security_query.update(security)
        else:
            original_securities.append(security)

    
    if custom_security_header:
        custom_securities.append(custom_security_header)
    if custom_security_query:
        custom_securities.append(custom_security_query)

    return original_securities + custom_securities