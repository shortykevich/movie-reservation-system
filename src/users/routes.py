from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.schemas import UserResponse, UserProfileResponse, UserCreateRequest
from src.users.utils import get_role_name_by_id, get_role_id_by_name
from src.users.models import User, RoleName
from src.auth.dependencies import get_current_active_user, has_roles
from src.database import get_async_db_session
from src.utils.passwords import get_user_with_hashed_pwd

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponse],
    dependencies=[has_roles([RoleName.admin, RoleName.staff])],
)
async def read_all_users(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> list[UserResponse]:
    stmt = select(User)
    db_response = await db.execute(stmt)
    users = db_response.scalars().all()
    return [UserResponse.model_validate(user) for user in users]


@router.get("/me", response_model=UserProfileResponse)
async def read_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
) -> UserProfileResponse:
    user_dict_info = current_user.model_dump()
    role_name = get_role_name_by_id(user_dict_info.pop('role_id'))
    user_dict_info.update({'role': role_name})
    print(user_dict_info)
    return UserProfileResponse.model_validate(user_dict_info)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
async def signup(
        db: Annotated[AsyncSession, Depends(get_async_db_session)],
        new_user: UserCreateRequest
) -> UserResponse:
    user_req = get_user_with_hashed_pwd(new_user)
    role_id = get_role_id_by_name(user_req.pop('role'))
    user_req.update({'role_id': role_id})

    stmt = insert(User).values(**user_req).returning(User)
    db_response = await db.execute(stmt)
    created_user = db_response.scalar_one()
    user_response = UserResponse.model_validate(created_user)
    await db.commit()
    return user_response
