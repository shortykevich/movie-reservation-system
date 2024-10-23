from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.schemas import UserResponse, UserProfileResponse, UserCreateRequest
from src.users.utils import get_role_name_by_id, get_role_id_by_name
from src.users.models import User, RoleName
from src.dependencies import get_current_user, requires_roles
from src.database import get_async_db_session
from src.utils.passwords import hash_user_pwd
from src.users.repository import UsersRepository

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponse],
    dependencies=[requires_roles([RoleName.admin, RoleName.staff])],
)
async def read_all_users(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> list[UserResponse]:
    users_repo = UsersRepository(db)
    return await users_repo.get_users()


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserProfileResponse)
async def read_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserProfileResponse:
    user_dict_info = current_user.model_dump()
    role_name = get_role_name_by_id(user_dict_info.pop("role_id"))
    user_dict_info.update({"role": role_name})
    print(user_dict_info)
    return UserProfileResponse.model_validate(user_dict_info)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def signup(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    new_user: UserCreateRequest,
) -> UserResponse:
    users_repository = UsersRepository(db)
    created_user = await users_repository.create_customer_user(new_user)
    return created_user
