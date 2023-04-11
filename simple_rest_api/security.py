'''Security scheme definitions'''

import logging
from typing import Optional, Any
from fastapi import HTTPException, Request, status, params, Security, Depends
from fastapi.security import APIKeyHeader, APIKeyQuery

from . import config
from .tempstorage import pseudo_keystore
from .models.api_credentials import ApiKeyEntry, ApiKeyRole, ApiKeyLevel, ApiKeyRoleComparison


LOG = logging.getLogger(__name__)


class ApiKeyAuthScheme:
    '''Custom paired API key authentication scheme'''

    query_key_scheme_name = 'ApiKeyQuery'
    query_app_scheme_name = 'AppNameQuery'
    header_key_scheme_name = 'ApiKeyHeader'
    header_app_scheme_name = 'AppNameHeader'

    api_key_query = APIKeyQuery(name=config.Security.Query.api_key, auto_error=False, scheme_name=query_key_scheme_name)
    app_name_query = APIKeyQuery(name=config.Security.Query.app_name, auto_error=False, scheme_name=query_app_scheme_name)
    api_key_header = APIKeyHeader(name=config.Security.Headers.api_key, auto_error=False, scheme_name=header_key_scheme_name)
    app_name_header = APIKeyHeader(name=config.Security.Headers.app_name, auto_error=False, scheme_name=header_app_scheme_name)

    def __init__(
        self,
        required_level: Optional[ApiKeyLevel]=None,
        required_roles: Optional[ApiKeyRole]=None,
        roles_comparison=ApiKeyRoleComparison.any
    ) -> None:
        self.required_roles = required_roles
        self.required_level = required_level
        self.roles_comparison = roles_comparison

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
        elif self.required_level and not request.state.api_key.has_required_level(self.required_level):
            LOG.warning('API key has inadequate level: %s', request.state.api_key)
            LOG.warning('Required level was %s', self.required_level)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized"
            )
        elif self.required_roles and not request.state.api_key.has_required_roles(self.required_roles, self.roles_comparison):
            LOG.warning('API key does not have required roles: %s', request.state.api_key)
            LOG.warning('Required roles were %s [%s]', self.required_roles, self.roles_comparison)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized"
            )

        LOG.debug('API key is valid and meets requirements for level=%s, roles=%s: %s', self.required_level, self.required_roles, request.state.api_key)

        return request.state.api_key


def qapi_key_dependency(
    required_level: Optional[ApiKeyLevel]=None,
    required_roles: Optional[ApiKeyRole]=None,
    roles_comparison=ApiKeyRoleComparison.any
) -> params.Depends:
    '''Convenience method for creating a `ApiKeyAuthScheme` dependency.

    Used without any arguments, this method simply returns a requirement for a valid
    API key of any level with any role entitlement.

    Routing dependencies are accumulative, so using a base-level access restriction on a router,
    then later adding to those requirements for each endpoint is completely fine and encouraged.

    Args:
        required_level (ApiKeyLevel, optional): Required access level, if applicable.
        required_roles (ApiKeyRole, optional): Required access roles, if applicable. Join multiple requirements with the bitwise XOR operator (|).
        roles_comparison (ApiKeyRoleComparison, optional): How should we compare the required access roles against key entitlements?
            Defaults to ApiKeyRoleComparison.any.

            Keys that have `ApiKeyRole.all` entitlement will always have access, regardless of `required_roles` and `roles_comparison` settings.

    Returns:
        Depends: Dependency ready for use with FastAPI routers and routing decorators
    '''

    return Depends(
        ApiKeyAuthScheme(
            required_level=required_level,
            required_roles=required_roles,
            roles_comparison=roles_comparison
        )
    )


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