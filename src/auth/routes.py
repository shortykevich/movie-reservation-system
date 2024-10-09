from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from sqlalchemy import insert, select

from src.users.models import User
from src.database import db_dependency
from src.auth.schemas import Token
from src.users.schemas import UserCreateRequest, UserResponse
from src.auth.core import (
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_active_user,
)
from src.exceptions import WrongCredentialException
from src.utils.passwords import get_user_with_hashed_pwd


router = APIRouter(tags=["auth"])


@router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
async def signup(db: db_dependency, new_user: UserCreateRequest) -> UserResponse:
    user_req = get_user_with_hashed_pwd(new_user)
    stmt = insert(User).values(**user_req).returning(User)
    db_response = await db.execute(stmt)
    created_user = db_response.scalar_one()
    user_response = UserResponse.model_validate(created_user)
    await db.commit()
    return user_response


@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(
    db: db_dependency,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise WrongCredentialException
    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me", response_model=UserResponse)
async def read_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
):
    return current_user
