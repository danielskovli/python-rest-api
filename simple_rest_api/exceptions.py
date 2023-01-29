'''Custom exceptions'''

from fastapi import HTTPException, status


# General exceptions
class SimpleRestApiError(Exception):
    '''Base class for all custom exceptions'''

class DuplicateAppNameError(SimpleRestApiError):
    '''The supplied app name is not unique'''

class InvalidApiKey(SimpleRestApiError):
    '''API is not valid and was rejected by the system'''


# HTTP errors
class UnauthorizedError(HTTPException):
    def __init__(self, detail: str='Unauthorized') -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class ConfigError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)