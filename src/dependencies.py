from typing import Annotated, Union, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import AccessTokenData
from src.auth.services import AuthenticationService
from src.exceptions import UnauthorizedError
from src.users.models import RoleName
from src.users.schemas import UserResponse
from src.database import get_async_db_session


auth_service = AuthenticationService()


def get_current_user(
    token: Annotated[Union[str, bytes], Depends(auth_service.oauth2_scheme)],
) -> AccessTokenData:
    """
    Retrieves the current authenticated user based on the provided JWT token.

    This dependency extracts the JWT token from the request using the OAuth2
    authentication scheme and verifies its validity.
    """
    return auth_service.verify_access_token(token)


async def get_current_user_from_db(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    token: Annotated[Union[str, bytes], Depends(auth_service.oauth2_scheme)],
) -> UserResponse:
    """
    Extends get_current_user dependency.
    Fetch the user's details from the database using the token's information.
    """
    return await auth_service.get_user_from_access_token(db, token)


def requires_roles(*roles: RoleName) -> Any:
    """
    Returns a ready-to-inject dependency for role-based access control.

    Example:
    ADMIN = RoleName.admin

    @router.get("/", dependencies=[requires_roles(ADMIN)])
    async def admin_dashboard(): ...

    Note:
        This function uses the `Depends()` internally to inject the `role_checker`
        dependency, so you DO NOT need to explicitly use `Depends()` when applying it.
    """

    async def role_checker(
        current_user: Annotated[AccessTokenData, Depends(get_current_user)]
    ) -> bool:
        if current_user.role not in (role.value for role in roles):
            raise UnauthorizedError(
                detail="Authorization failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return True

    return Depends(role_checker)
