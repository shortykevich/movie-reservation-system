from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.users.models import RoleName


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    phone_number: PhoneNumber = Field(min_length=11)
    email: EmailStr = Field(min_length=3, max_length=100)
    first_name: Optional[str] = Field(max_length=50)
    last_name: Optional[str] = Field(max_length=50)


class UserCreateRequest(UserBase):
    password: str = Field(min_length=8, max_length=100)
    # role: RoleName = Field(default=RoleName.customer)


class UserResponse(UserBase):
    role_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(UserBase):
    role: RoleName

    model_config = ConfigDict(from_attributes=True)
