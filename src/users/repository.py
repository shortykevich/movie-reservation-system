from typing import Optional

from fastapi import status, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, Select, update

from src.users.models import User, RoleName
from src.users.schemas import UserCreateRequest, UserResponse, UserUpdateRequest
from src.users.utils import get_role_id_by_name
from src.utils.passwords import hash_user_pwd


class UsersRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, stmt: Select) -> Optional[UserResponse]:
        entity = (await self.db.execute(stmt)).scalar_one_or_none()
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return UserResponse.model_validate(entity)

    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        stmt = select(User).where(User.id == user_id)
        return await self.get_user(stmt)

    async def get_user_by_name(self, username: str) -> Optional[UserResponse]:
        stmt = select(User).where(User.username == username)
        return await self.get_user(stmt)

    async def get_users(self) -> list[UserResponse]:
        stmt = select(User)
        users = (await self.db.execute(stmt)).scalars().all()
        return [UserResponse.model_validate(user) for user in users]

    async def create_customer_user(self, user: UserCreateRequest) -> UserResponse:
        user_data = hash_user_pwd(user)
        customer_role_id = get_role_id_by_name(RoleName.customer)
        user_data.update({"role_id": customer_role_id})

        stmt = insert(User).values(**user_data).returning(User)
        try:
            db_response = await self.db.execute(stmt)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Wrong data"
            )
        new_user = db_response.scalar_one()
        user_response = UserResponse.model_validate(new_user)
        await self.db.commit()
        return user_response

    async def update_user(
        self, user_data: UserUpdateRequest, user_id: int
    ) -> UserResponse:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**user_data.model_dump(exclude_unset=True))
            .returning(User)
        )
        try:
            db_response = await self.db.execute(stmt)
        except SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        new_user = db_response.scalar_one()
        user_response = UserResponse.model_validate(new_user)
        await self.db.commit()
        return user_response
