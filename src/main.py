from fastapi import FastAPI


from src.auth.routes import router as auth_router
from src.users.routes.admin_routes import router as admin_router
from src.users.routes.user_routes import router as users_router


# @asynccontextmanager
# async def lifespan(_: FastAPI):
#     """Startup and shutdown events handler"""
#     db_session_manager = DBAsyncSessionManager(settings.get_database_url())
#     async with db_session_manager.session() as session:
#         *ON STARTUP ACTIONS*
#         yield
#         *ON SHUTDOWN ACTIONS*


app = FastAPI()


app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(users_router)
