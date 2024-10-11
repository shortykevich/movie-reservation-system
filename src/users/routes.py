from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.schemas import UserResponse, UserProfileResponse
from src.users.utils import get_role_name_by_id
from src.users.models import User
from src.auth.dependencies import get_current_active_user
from src.database import get_db_session
from src.exceptions import UnauthorizedException

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponse]
)
async def read_all_users(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
) -> list[UserResponse]:
    if not current_user.role_id == 1:
        raise UnauthorizedException
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
