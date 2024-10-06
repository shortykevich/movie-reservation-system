from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.config import settings


class Base(DeclarativeBase):
    pass


async_engine = create_async_engine(
    settings.get_database_url(),
    echo=True
)

async_session = async_sessionmaker(bind=async_engine)

async def async_db_connection() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


db_dependency = Annotated[AsyncSession, Depends(async_db_connection)]
