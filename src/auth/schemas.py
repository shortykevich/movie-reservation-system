from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    issued_at: Optional[datetime] = None
    expires_in: Optional[datetime] = None


class AccessTokenData(TokenData):
    role: Optional[str] = None


class RefreshTokenData(TokenData):
    pass
