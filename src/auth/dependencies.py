from typing import Annotated, Union

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services import AuthenticationService
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
