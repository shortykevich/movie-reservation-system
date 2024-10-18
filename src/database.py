from typing import Optional, AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
    AsyncConnection
)

from src.config import settings


class Base(DeclarativeBase):
    pass


class DBSessionManager:
    _engine: Optional[AsyncEngine] = create_async_engine(
        settings.get_database_url(),
        echo=True
    )
    _sessionmaker: Optional[async_sessionmaker[AsyncSession]] = async_sessionmaker(
        autocommit=False, bind=_engine
    )

    async def close(self) -> None:
        if not self._engine:
            raise SQLAlchemyError
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if not self._engine:
            raise SQLAlchemyError

        async with self._engine.begin() as connection:
            try:
                yield connection
            except SQLAlchemyError as e:
                await connection.rollback()
                raise e

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if not self._sessionmaker:
            raise SQLAlchemyError

        async with self._sessionmaker() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        return cls._engine


async def get_db_session() -> AsyncSession:
    sessionmanager = DBSessionManager()
    async with sessionmanager.session() as session:
        yield session
