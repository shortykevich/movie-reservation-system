from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

from src.constants import ROLES_MAPPING
from src.database import DBAsyncSessionManager
from src.users.models import Role
from src.auth.routes import router as auth_router
from src.users.routes import router as users_router
from src.config import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Startup and shutdown events handler"""
    db_session_manager = DBAsyncSessionManager(settings.get_database_url())
    async with db_session_manager.session() as session:
        stmt = select(Role)
        roles = (await session.execute(stmt)).scalars().fetchall()
        ROLES_MAPPING.update({role.name: role.id for role in roles})
        await session.close()
        yield
        ROLES_MAPPING.clear()


app = FastAPI(lifespan=lifespan)


app.include_router(auth_router)
app.include_router(users_router)
