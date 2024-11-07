from typing import Optional, Any

from starlette import status
from fastapi import HTTPException


class WrongCredentialError(HTTPException):
    def __init__(self, detail: Any, headers: Optional[dict[str, str]] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers
        )


class UserInactiveError(HTTPException):
    def __init__(self, detail: Any):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: Any, headers: Optional[dict[str, str]] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers
        )


class InvalidTokenTypeError(HTTPException):
    def __init__(self, detail: Any):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class TokenExpiredError(HTTPException):
    def __init__(self, detail: Any):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InvalidTokenDataError(HTTPException):
    def __init__(self, detail: Any):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
