from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

from src.config import settings
from src.constants import ROLES_MAPPING
from src.database import get_db_session, DBSessionManager
from src.users.models import Role
from src.auth.routes import router as auth_router
from src.users.routes import router as users_router


@asynccontextmanager
async def map_roles(app: FastAPI):
    db_session_manager = DBSessionManager(settings.get_database_url())
    async with db_session_manager.session() as session:
        stmt = select(Role)
        result = await session.execute(stmt)
        roles = result.scalars().fetchall()
        ROLES_MAPPING.update({role.name: role.id for role in roles})
        yield
        ROLES_MAPPING.clear()


app = FastAPI(lifespan=map_roles)


app.include_router(auth_router)
app.include_router(users_router)
