from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    first_name: Optional[str] = Field(max_length=50)
    last_name: Optional[str] = Field(max_length=50)
    email: EmailStr = Field(min_length=3, max_length=100)


class UserCreateRequest(UserBase):
    password: str = Field(min_length=8, max_length=100)
    role_id: int = Field(default=3)

class UserResponse(UserBase):
    id: int
    is_active: bool
    role_id: int

    model_config = ConfigDict(from_attributes=True)
