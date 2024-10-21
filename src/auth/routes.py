from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database import get_async_db_session
from src.auth.schemas import Token
from src.dependencies import auth_service
from src.exceptions import UserInactiveException

router = APIRouter(tags=["auth"])


@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await auth_service.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise UserInactiveException
    access_token = auth_service.create_access_token(user)
    return Token(access_token=access_token)
