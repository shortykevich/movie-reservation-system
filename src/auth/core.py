import jwt
from datetime import timedelta, datetime, timezone
from typing import Annotated, Optional, Union

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import UserInactiveException, WrongCredentialException
from src.auth.schemas import TokenData
from src.users.schemas import UserResponse
from src.auth.config import token_settings
from src.users.models import User
from src.database import get_db_session
from src.utils.passwords import verify_pwd


PRIVATE_KEY = token_settings.get_private_key()
PUBLIC_KEY = token_settings.get_public_key()
ALGORITHM = token_settings.get_algorithm()
ACCESS_TOKEN_EXPIRE_MINUTES = token_settings.get_access_token_expires_in()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def encode_jwt(
    payload: dict,
    private_key: str = PRIVATE_KEY,
    algorithm: str = ALGORITHM,
) -> str:
    return jwt.encode(payload, private_key, algorithm=algorithm)


def decode_jwt(
    token: Annotated[Union[str, bytes], Depends(oauth2_scheme)],
    public_key: str = PUBLIC_KEY,
    algorithm: str = ALGORITHM,
) -> dict:
    return jwt.decode(token, public_key, algorithms=[algorithm])


async def get_user(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    username: str
) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    user = await db.execute(stmt)
    return user.scalar_one_or_none()


async def authenticate_user(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    username: str,
    password: str,
) -> Union[UserResponse, bool]:
    user = await get_user(db, username)
    if not user or not verify_pwd(password, user.password):
        return False
    return UserResponse.model_validate(user)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return encode_jwt(to_encode)


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    token: Annotated[Union[str, bytes], Depends(oauth2_scheme)],
) -> UserResponse:
    try:
        payload = decode_jwt(token)
        username: str = payload.get("sub")
        if not username:
            raise WrongCredentialException
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise WrongCredentialException
    user = await get_user(db, username=token_data.username)
    if not user:
        raise WrongCredentialException
    return UserResponse.model_validate(user)


async def get_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserResponse:
    if not current_user.is_active:
        raise UserInactiveException
    return current_user
