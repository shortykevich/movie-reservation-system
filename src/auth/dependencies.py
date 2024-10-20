from typing import Annotated, Union

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services import AuthenticationService
from src.users.models import RoleName
from src.users.schemas import UserResponse
from src.database import get_async_db_session


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

# Template for authorization control:

# def has_roles(required_roles: list[RoleName]):
#     def decorator(func):
#         async def wrapper(*args, **kwargs):
#             user = await get_current_active_user()
#             if user.role not in required_roles:
#                 raise HTTPException(
#                     status_code=403,
#                     detail="Ye shall not pass!"
#                 )
#             return await func(*args, **kwargs)
#         return wrapper
#     return decorator
