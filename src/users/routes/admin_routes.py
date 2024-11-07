from typing import Annotated

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import ADMIN
from src.database import get_async_db_session
from src.dependencies import requires_roles
from src.users.repository import UsersRepository
from src.users.schemas import UserUpdateRequest, UserResponse

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[requires_roles(ADMIN)],
)


@router.get(
    "/users/",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponse],
)
async def read_all_users(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> list[UserResponse]:
    users = await UsersRepository(db).get_users_paginated()
    return [UserResponse.model_validate(user) for user in users]


@router.patch(
    "/{user_id}/",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def update_user_info(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    new_user_data: UserUpdateRequest,
    user_id: int,
) -> UserResponse:
    updated_user = await UsersRepository(db).update_user(new_user_data, user_id)
    return UserResponse.model_validate(updated_user)


@router.get(
    "/{user_id}/",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def read_user_by_id(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
):
    user = await UsersRepository(db).get_user_by_id(user_id)
    return UserResponse.model_validate(user)
