from typing import Optional, Union

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select, update, ScalarSelect, Result
from sqlalchemy.sql.dml import ReturningInsert, ReturningUpdate

from src.users.exceptions import UserNotFoundError, UserDataError, CreationError
from src.users.models import User, RoleName, Role
from src.users.schemas import UserCreateRequest, UserUpdateRequest
from src.utils.passwords import hash_user_pwd


class UsersRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def get_role_id_subquery(role: RoleName) -> ScalarSelect[User]:
        """Subquery for getting role id using role name"""
        return select(Role.id).where(Role.name == role).scalar_subquery()

    async def execute_stmt(
        self,
        stmt: Union[Select, ReturningInsert, ReturningUpdate],
        error: Optional[Exception] = None,
    ) -> Result:
        try:
            db_response = await self.db.execute(stmt)
        except SQLAlchemyError:
            raise error
        return db_response

    async def get_user(self, stmt: Select) -> User:
        db_response = await self.execute_stmt(
            stmt=stmt, error=UserNotFoundError(detail="User not found")
        )
        return db_response.scalar_one()

    async def get_user_by_id(self, user_id: int) -> User:
        stmt = select(User).where(User.id == user_id)
        return await self.get_user(stmt)

    async def get_user_by_name(self, username: str) -> User:
        stmt = select(User).where(User.username == username)
        return await self.get_user(stmt)

    async def get_users(self) -> list[User]:
        stmt = select(User)
        db_response = await self.execute_stmt(stmt)
        users = db_response.scalars().all()
        return [user for user in users]

    async def create_user(
        self, user: UserCreateRequest, role: RoleName = RoleName.customer
    ) -> User:
        user_data = hash_user_pwd(user)
        db_response = await self.db.execute(select(Role).where(Role.name == role))

        role_obj = db_response.scalar_one()
        new_user = User(**user_data, role=role_obj)

        try:
            self.db.add(new_user)
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            raise CreationError(exception=e)

        return new_user

    async def update_user(self, user_data: UserUpdateRequest, user_id: int) -> User:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**user_data.model_dump(exclude_unset=True, exclude_none=True))
            .returning(User)
        )
        db_response = await self.execute_stmt(
            stmt=stmt, error=UserDataError(detail="Wrong user data")
        )
        updated_user = db_response.scalar_one()
        await self.db.commit()
        await self.db.refresh(updated_user)
        return updated_user

    async def deactivate_user(self, user_id: int) -> User:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
            .returning(User)
        )
        db_response = await self.execute_stmt(
            stmt=stmt, error=UserDataError(detail="Wrong user data")
        )
        updated_user = db_response.scalar_one()
        await self.db.commit()
        await self.db.refresh(updated_user)
        return updated_user
