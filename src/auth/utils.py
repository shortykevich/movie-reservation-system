import jwt
from datetime import timedelta, datetime, timezone
from typing import Annotated, Optional, Union

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy import select
from starlette import status

from src.auth.schemas import TokenData, UserResponse
from src.config import token_settings
from src.auth.models import User
from src.database import db_dependency
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
):
    return jwt.encode(payload, private_key, algorithm=algorithm)


def decode_jwt(
    token: Annotated[Union[str, bytes], Depends(oauth2_scheme)],
    public_key: str = PUBLIC_KEY,
    algorithm: str = ALGORITHM,
):
    return jwt.decode(token, public_key, algorithms=[algorithm])


async def get_user(
    db: db_dependency,
    username: str
) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    user = await db.execute(stmt)
    return user.scalar_one_or_none()


async def authenticate_user(
    db: db_dependency,
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
    db: db_dependency,
    token: Annotated[Union[str, bytes], Depends(oauth2_scheme)],
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Wrong credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode_jwt(token)
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(db, username=token_data.username)
    if not user:
        raise credentials_exception
    return UserResponse.model_validate(user)


async def get_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
