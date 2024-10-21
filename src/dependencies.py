from typing import Annotated, Union, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services import AuthenticationService
from src.exceptions import UnauthorizedException
from src.users.models import RoleName
from src.users.schemas import UserResponse
from src.database import get_async_db_session
from src.users.utils import get_role_name_by_id


auth_service = AuthenticationService()


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    token: Annotated[Union[str, bytes], Depends(auth_service.oauth2_scheme)],
) -> UserResponse:
    """
    Retrieves the current authenticated user based on the provided JWT token.

    This dependency extracts the JWT token from the request using the OAuth2
    authentication scheme and verifies its validity. It then fetches the user's
    details from the database using the token's information.
    """
    return await auth_service.get_current_user(db, token)


def requires_roles(roles_list: list[RoleName]) -> Any:
    """
    Returns a ready-to-inject dependency for role-based access control.

        Examples:
        Using the dependency directly in route definition:

        1. In a route decorator:

        @router.get("/", dependencies=[requires_roles([RoleName.admin])])
        async def admin_dashboard(): ...

        2. As an argument annotation in route functions (Recommended for consistency):

        @router.get("/admin")
        async def admin_dashboard(
            current_user: Annotated[UserResponse, requires_roles([RoleName.admin])]
        ): ...

    Note:
        This function uses the `Depends()` internally to inject the `role_checker`
        dependency, so you do not need to explicitly use `Depends()` when applying it.
    """

    async def role_checker(
        current_user: Annotated[UserResponse, Depends(get_current_user)]
    ) -> UserResponse:
        if get_role_name_by_id(current_user.role_id) not in roles_list:
            raise UnauthorizedException
        return current_user

    return Depends(role_checker)
