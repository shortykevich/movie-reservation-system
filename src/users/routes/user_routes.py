from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import AccessTokenData
from src.users.schemas import (
    UserResponse,
    UserUpdateRequest,
    RawUserResponse,
)
from src.dependencies import get_current_user_from_db, get_current_user_from_jwt
from src.database import get_async_db_session
from src.users.repository import UsersRepository

router = APIRouter(
    prefix="/users/me",
    tags=["users"],
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def read_current_active_user(
    current_user: Annotated[RawUserResponse, Depends(get_current_user_from_db)],
) -> UserResponse:
    user_data = current_user.model_dump()
    return UserResponse.model_validate(user_data)


@router.patch(
    "/update/",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def update_current_user_data(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    current_user: Annotated[AccessTokenData, Depends(get_current_user_from_jwt)],
    update_request: UserUpdateRequest,
):
    updated_user = await UsersRepository(db).update_user(
        update_request, current_user.id
    )
    return UserResponse.model_validate(updated_user)


@router.patch(
    "/deactivate/",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def deactivate_user(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    current_user: Annotated[AccessTokenData, Depends(get_current_user_from_jwt)],
) -> UserResponse:
    updated_user = await UsersRepository(db).deactivate_user(current_user.id)
    return UserResponse.model_validate(updated_user)
