from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.schemas import UserResponse
from src.users.models import User
from src.auth.core import get_current_active_user
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
    if not current_user.role_id in range(1, 3):
        raise UnauthorizedException
    stmt = select(User)
    db_response = await db.execute(stmt)
    users = db_response.scalars().all()
    return [UserResponse.model_validate(user) for user in users]
