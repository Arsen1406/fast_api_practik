from fastapi import Depends, status, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from app.models.models import User

users_bd = [
    User(username="vasya", password="31maet"),
    User(username="masha", password="qwerty"),
    User(**{"username": "user1", "password": "pass1"}),
    User(**{"username": "user2", "password": "pass2"})
]

security = HTTPBasic()


def get_user_from_db(username) -> User | None:
    for user in users_bd:
        if user.username == username:
            return user
    return None


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = get_user_from_db(credentials.username)
    if user is None or user.password != credentials.password:
        content = "Invalid credentials"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=content
        )
    return user
