from fastapi import FastAPI

from src.auth.routes import router as auth_router
from src.users.routes import router as users_router


app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
