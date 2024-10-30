from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database import get_async_db_session
from src.auth.schemas import Token
from src.dependencies import auth_service
from src.exceptions import WrongCredentialError


http_bearer = HTTPBearer()
router = APIRouter(tags=["auth"])


@router.post("/token/", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await auth_service.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise WrongCredentialError(detail="Wrong credentials")
    access_token = auth_service.create_access_token(user)
    refresh_token = auth_service.create_refresh_token(user)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh/",
    response_model=Token,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def refresh_access_token(
    db: Annotated[AsyncSession, Depends(get_async_db_session)],
    refresh_token: Annotated[
        Optional[HTTPAuthorizationCredentials], Depends(http_bearer)
    ],
) -> Token:
    new_access_token = await auth_service.refresh_access_token(
        db, refresh_token.credentials
    )
    return Token(
        access_token=new_access_token,
    )
