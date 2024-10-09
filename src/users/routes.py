from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from src.users.schemas import UserResponse
from src.users.models import User
from src.auth.core import get_current_active_user
from src.database import db_dependency
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
    db: db_dependency,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
) -> list[UserResponse]:
    if not current_user.role_id in range(1, 3):
        raise UnauthorizedException
    stmt = select(User)
    users = await db.execute(stmt)
    return users.scalars().all()
