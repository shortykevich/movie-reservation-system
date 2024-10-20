from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy import insert

from src.users.models import User
from src.database import get_async_db_session
from src.auth.schemas import Token
from src.users.schemas import UserCreateRequest, UserResponse
from src.auth.dependencies import auth_service
from src.exceptions import WrongCredentialException
from src.utils.passwords import get_user_with_hashed_pwd
from src.users.utils import get_role_id_by_name, get_role_name_by_id

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
        raise WrongCredentialException
    access_token = auth_service.create_access_token(user)
    return Token(access_token=access_token, token_type="bearer")
