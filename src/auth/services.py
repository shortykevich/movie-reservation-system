import jwt
from datetime import timedelta, datetime, timezone
from typing import Optional, Union

from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import UserInactiveException, WrongCredentialException
from src.auth.schemas import TokenData
from src.users.schemas import UserResponse
from src.auth.config import token_settings
from src.users.models import User
from src.users.utils import get_role_name_by_id
from src.utils.passwords import verify_pwd


class AuthenticationService:
    def __init__(self):
        self.private_key = token_settings.get_private_key()
        self.public_key = token_settings.get_public_key()
        self.algorithm = token_settings.get_algorithm()
        self.access_token_expire_minutes = token_settings.get_access_token_expires_in()
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    def encode_jwt(self, payload: dict) -> str:
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    def decode_jwt(self, token: Union[str, bytes]) -> dict:
        return jwt.decode(token, self.public_key, algorithms=[self.algorithm])

    async def get_user(
            self, db: AsyncSession, username: str
    ) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        user = await db.execute(stmt)
        return user.scalar_one_or_none()

    async def authenticate_user(
            self, db: AsyncSession, username: str, password: str
    ) -> Union[UserResponse, bool]:
        user = await self.get_user(db, username)
        if not user or not verify_pwd(password, user.password):
            return False
        return UserResponse.model_validate(user)

    def create_access_token(self, user: UserResponse) -> str:
        expire = (
            datetime.now(timezone.utc) +
            timedelta(minutes=self.access_token_expire_minutes)
        )
        to_encode ={
            "sub": user.username,
            "role": get_role_name_by_id(user.role_id).name,
            "iat": datetime.now(timezone.utc),
            "exp": expire
        }
        return self.encode_jwt(to_encode)

    async def get_current_user(
            self, db: AsyncSession, token: Union[str, bytes]
    ) -> UserResponse:
        try:
            payload = self.decode_jwt(token)
            username: str = payload.get("sub")
            if not username:
                raise WrongCredentialException
            token_data = TokenData(username=username)
        except InvalidTokenError:
            raise WrongCredentialException
        user = await self.get_user(db, username=token_data.username)
        if not user:
            raise WrongCredentialException
        return UserResponse.model_validate(user)

    async def get_current_active_user(
            self, current_user: UserResponse
    ) -> UserResponse:
        if not current_user.is_active:
            raise UserInactiveException
        return current_user
