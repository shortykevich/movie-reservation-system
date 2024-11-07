from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from src.database import get_async_db_session
from src.auth.schemas import AccessToken, SignUpScheme
from src.dependencies import auth_service
from src.users.repository import UsersRepository
from src.users.schemas import UserResponse, UserCreateRequest

http_bearer = HTTPBearer(auto_error=False)
router = APIRouter(tags=["auth"])


@router.post(
    "/signup/",
    status_code=status.HTTP_201_CREATED,
    response_model=SignUpScheme,
)
async def signup(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    new_user: UserCreateRequest,
    response: Response,
) -> SignUpScheme:
    created_user = UserResponse.model_validate(
        await UsersRepository(db).create_user(new_user)
    )
    access_token = AccessToken(
        access_token=auth_service.create_access_token(created_user)
    )
    refresh_token = auth_service.create_refresh_token(created_user)
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        max_age=auth_service.cookie_expire_seconds,
    )
    return SignUpScheme(user=created_user, token=access_token)


@router.post("/token/", status_code=status.HTTP_200_OK, response_model=AccessToken)
async def login_for_access_token(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
) -> AccessToken:
    user = await auth_service.authenticate_user(
        db, form_data.username, form_data.password
    )
    access_token = AccessToken(access_token=auth_service.create_access_token(user))
    refresh_token = auth_service.create_refresh_token(user)
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        max_age=auth_service.cookie_expire_seconds,
    )
    return access_token


@router.post("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie("refresh_token")
    return None


@router.post("/refresh/", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    request: Request,
) -> AccessToken:
    refresh_token = auth_service.get_refresh_token_from_request(request)
    new_access_token = await auth_service.refresh_access_token(db, refresh_token)
    return AccessToken(access_token=new_access_token)
