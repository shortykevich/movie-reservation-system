from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    first_name: Optional[str] = Field(max_length=50)
    last_name: Optional[str] = Field(max_length=50)
    email: EmailStr = Field(min_length=3, max_length=100)


class UserRequest(UserBase):
    password: str = Field(min_length=8, max_length=100)
    role_id: int = Field(default=3, description="Optional field. Only for admin/staff creating.\n"
                                                "admin(id=1), staff(id=2), user(id=3)")

class UserResponse(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    role_id: Optional[int] = None
