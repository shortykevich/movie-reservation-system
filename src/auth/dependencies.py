from typing import Annotated, Union

from fastapi import Depends, HTTPException
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
    return await auth_service.get_current_user(db, token)


async def get_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserResponse:
    return await auth_service.get_current_active_user(current_user)


def has_roles(required_roles: list[RoleName]):
    async def role_checker(
        current_user: Annotated[UserResponse, Depends(get_current_active_user)]
    ):
        if get_role_name_by_id(current_user.role_id) not in required_roles:
            raise UnauthorizedException
        return current_user

    return Depends(role_checker)
