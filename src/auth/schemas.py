from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.users.schemas import UserResponse


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    issued_at: Optional[datetime] = None
    expires_in: Optional[datetime] = None


class AccessTokenData(TokenData):
    id: Optional[int] = None
    role: Optional[str] = None


class RefreshTokenData(TokenData):
    pass


class SignUpScheme(BaseModel):
    user: UserResponse
    token: AccessToken
