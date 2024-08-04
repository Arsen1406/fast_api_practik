from fastapi import FastAPI
from app.routers import users

app = FastAPI(title="my_app", version="v1")
app.include_router(users.app)
