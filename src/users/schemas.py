from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.users.models import RoleName


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    phone_number: PhoneNumber = Field(min_length=11)
    email: EmailStr = Field(min_length=3, max_length=100)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)

    model_config = ConfigDict(from_attributes=True)


class RoleScheme(BaseModel):
    name: RoleName

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    id: int
    is_active: bool
    role_id: int
    role: Optional[RoleScheme]


class RawUserResponse(UserResponse):
    password: str
    created_at: datetime
    updated_at: datetime


class UserCreateRequest(UserBase):
    password: str = Field(min_length=8, max_length=100)


class UserUpdateRequest(UserBase):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone_number: Optional[PhoneNumber] = Field(None, min_length=11)
    email: Optional[EmailStr] = Field(None, min_length=3, max_length=100)
