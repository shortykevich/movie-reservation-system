import jwt
from datetime import timedelta, datetime, timezone
from typing import Optional, Union

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.auth.constants import TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from src.exceptions import (
    WrongCredentialError,
    InvalidTokenTypeError,
    TokenExpiredError,
    UserInactiveError,
    InvalidTokenDataError,
)
from src.auth.schemas import AccessTokenData, RefreshTokenData
from src.users.schemas import UserResponse
from src.auth.config import jwt_settings
from src.users.models import User
from src.users.utils import get_role_name_by_id
from src.utils.passwords import verify_pwd


class AuthenticationService:
    def __init__(self):
        self.token_schemas = {
            ACCESS_TOKEN_TYPE: AccessTokenData,
            REFRESH_TOKEN_TYPE: RefreshTokenData,
        }
        self.private_key = jwt_settings.get_private_key()
        self.public_key = jwt_settings.get_public_key()
        self.algorithm = jwt_settings.get_algorithm()
        self.access_token_expire_minutes = (
            jwt_settings.get_access_token_expires_in_minutes()
        )
        self.refresh_token_expire_minutes = (
            jwt_settings.get_refresh_token_expires_in_minutes()
        )
        self.cookie_expire_seconds = self.refresh_token_expire_minutes * 60
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    def encode_jwt(self, payload: dict) -> str:
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    def decode_jwt(self, token: Union[str, bytes]) -> dict:
        return jwt.decode(token, self.public_key, algorithms=[self.algorithm])

    def create_token(
        self,
        user: UserResponse,
        expires_delta: int,
        token_type: str,
    ) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
        to_encode = {
            TOKEN_TYPE_FIELD: token_type,
            "sub": user.username,
            "iat": datetime.now(timezone.utc),
            "exp": expire,
        }
        if token_type == ACCESS_TOKEN_TYPE:
            to_encode.update({"role": get_role_name_by_id(user.role_id).name})
        return self.encode_jwt(to_encode)

    def create_access_token(self, user: UserResponse) -> str:
        return self.create_token(
            user=user,
            expires_delta=self.access_token_expire_minutes,
            token_type=ACCESS_TOKEN_TYPE,
        )

    def create_refresh_token(self, user: UserResponse) -> str:
        return self.create_token(
            user=user,
            expires_delta=self.refresh_token_expire_minutes,
            token_type=REFRESH_TOKEN_TYPE,
        )

    @staticmethod
    def check_token_type(payload: dict, expected_type: str) -> bool:
        current_type = payload.get(TOKEN_TYPE_FIELD)
        if current_type != expected_type:
            raise InvalidTokenTypeError(
                detail=f"Invalid token type {current_type!r} is not {expected_type!r}"
            )
        return True

    @staticmethod
    def check_token_expiration(payload: dict, token_type: str) -> bool:
        expire_at = payload.get("exp")
        if expire_at is None:
            raise InvalidTokenDataError(
                detail=f"{token_type!r} token does not contain an expiration timestamp"
            )
        expire_at = datetime.fromtimestamp(expire_at, timezone.utc)
        if expire_at < datetime.now(timezone.utc):
            raise TokenExpiredError(detail=f"{token_type!r} is expired")
        return True

    def verify_token(
        self,
        token: Union[str, bytes],
        token_type: str,
    ) -> dict:
        try:
            payload = self.decode_jwt(token)
            self.check_token_type(payload, token_type)
            self.check_token_expiration(payload, token_type)

            username: str = payload.get("sub")
            if not username:
                raise WrongCredentialError(
                    detail="Wrong credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return payload
        except jwt.InvalidTokenError:
            raise WrongCredentialError(
                detail="Wrong credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def verify_access_token(self, token: Union[str, bytes]) -> AccessTokenData:
        payload = self.verify_token(token=token, token_type=ACCESS_TOKEN_TYPE)
        return AccessTokenData(
            username=payload.get("sub"),
            role=payload.get("role"),
            issued_at=payload.get("iat"),
            expires_in=payload.get("exp"),
        )

    def verify_refresh_token(self, token: Union[str, bytes]) -> RefreshTokenData:
        payload = self.verify_token(token=token, token_type=REFRESH_TOKEN_TYPE)
        return RefreshTokenData(
            username=payload.get("sub"),
            issued_at=payload.get("iat"),
            expires_in=payload.get("exp"),
        )

    async def refresh_access_token(
        self, db: AsyncSession, refresh_token: Union[str, bytes]
    ) -> str:
        token_data = self.verify_refresh_token(refresh_token)
        user = await self.get_user(db, token_data.username)
        self.is_user_active(user)
        if not user:
            raise WrongCredentialError(detail="Wrong credentials")
        return self.create_access_token(UserResponse.model_validate(user))

    @staticmethod
    async def get_user(db: AsyncSession, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        user = await db.execute(stmt)
        return user.scalar_one_or_none()

    @staticmethod
    def is_user_active(user: User) -> bool:
        if not user.is_active:
            raise UserInactiveError(detail="User is inactive")
        return True

    async def authenticate_user(
        self, db: AsyncSession, username: str, password: str
    ) -> UserResponse:
        user = await self.get_user(db, username)
        is_valid_pwd = verify_pwd(password, user.password)
        if not (user and is_valid_pwd and self.is_user_active(user)):
            raise WrongCredentialError(detail="Wrong credentials")
        return UserResponse.model_validate(user)

    async def get_user_from_access_token(
        self, db: AsyncSession, token: Union[str, bytes]
    ) -> UserResponse:
        token_data = self.verify_access_token(token)
        user = await self.get_user(db, username=token_data.username)
        if not user:
            raise WrongCredentialError(
                detail="Wrong credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserResponse.model_validate(user)

    @staticmethod
    def get_refresh_token_from_request(request: Request) -> Union[str, bytes]:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise WrongCredentialError(detail="Refresh token not found")
        return refresh_token
