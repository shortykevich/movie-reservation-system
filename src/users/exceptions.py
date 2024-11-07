from typing import Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status
from fastapi import HTTPException


class BaseError(HTTPException):
    _schema = {}

    def set_error(self, error: str):
        self._schema["error"] = error

    def set_message(self, message: str):
        self._schema["message"] = message

    def get_detail(self):
        return self._schema


class UserNotFoundError(BaseError):
    def __init__(self, detail: str, headers: Optional[dict[str, str]] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers
        )


class UserDataError(BaseError):
    def __init__(self, detail: str, headers: Optional[dict[str, str]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            headers=headers,
        )


class CreationError(BaseError):
    def __init__(
        self, exception: IntegrityError, headers: Optional[dict[str, str]] = None
    ):
        orig_exc = exception.orig

        # For psycopg lib:
        constraint_name = orig_exc.diag.constraint_name

        self.set_error("Duplicate Entry")
        self.set_message(f"{constraint_name!r} already exists")

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=self.get_detail(),
            headers=headers,
        )
