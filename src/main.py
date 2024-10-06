from fastapi import FastAPI

from src.auth.routes import router


app = FastAPI()

app.include_router(router)
