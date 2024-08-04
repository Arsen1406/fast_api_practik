from app.models.models import User, Product
from typing import Annotated
from fastapi import APIRouter, Header, Depends
from fastapi import Response, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from app.utils import authenticate_user

data = (
    {
        "product_id": 123,
        "name": "Smartphone",
        "category": "Electronics",
        "price": 599.99
    },
    {
        "product_id": 456,
        "name": "Phone Case Smartphone",
        "category": "Accessories",
        "price": 19.99
    },
    {
        "product_id": 789,
        "name": "Iphone Smartphone",
        "category": "Electronics",
        "price": 1299.99
    },
    {
        "product_id": 101,
        "name": "Headphones",
        "category": "Accessories",
        "price": 99.99
    },
    {
        "product_id": 202,
        "name": "Smartwatch",
        "category": "Electronics",
        "price": 299.99
    }
)
users_bd = [
    User(username="vasya", password="31maet"),
    User(username="masha", password="qwerty"),
    User(**{"username": "user1", "password": "pass1"}),
    User(**{"username": "user2", "password": "pass2"})
]

app = APIRouter()


def write_notification(pk: int, message: str = ""):
    with open("log.txt", mode="a+", encoding="utf-8") as email_file:
        print("ФОНОВАЯ ЗАДАЧА")
        res = email_file.read()
        content = f"Искали ID -> {pk}: {message}\n"
        email_file.write(res + content)


@app.get("/login/")
async def get_login(user: User = Depends(authenticate_user)):
    return {
        "message": "You have access to the protected resource!",
        "user_info": user
    }


@app.get("/headers/")
async def root(request: Request):
    headers = ("User-Agent", "Accept-Language")
    lang = "ru,en;q=0.9"
    response = dict()
    for name_header in headers:
        header = request.headers.get(name_header)
        if header is None:
            content = {"message": f"Не передан заголовок {name_header}"}
            return JSONResponse(status_code=400, content=content)

        if name_header == "Accept-Language" and header != lang:
            content = {
                "message": f"{name_header} не соответствует формату {lang}"
            }
            return JSONResponse(status_code=400, content=content)
        response[name_header] = header
    return response


@app.get("/items/")
async def read_items(user_agent: str = Header()):
    return {"user_agent": user_agent}


@app.post("/login/")
async def login(user: User, response: Response):
    search_user = [us for us in users_bd if us.username == user.username]
    if len(search_user) == 0:
        message = f"Пользователь {user.username} не зарегистрирован"
        raise HTTPException(status_code=401, detail=message)

    if user.password == search_user[0].password:
        token = str(user.username + user.password)
        response.set_cookie(key="session_token", value=token, httponly=True)
        content = {"message": "Вход выполнен"}
        return JSONResponse(status_code=200, content=content)
    raise HTTPException(status_code=401, detail="Неверный пароль!")


@app.get("/user/")
async def user_info(request: Request) -> User:
    user_token = request.cookies.get("session_token")
    for us in users_bd:
        if str(us.username + us.password) == user_token:
            return us

    content = "Пожалуйста авторизуйтесь в системе!"
    raise HTTPException(status_code=401, detail=content)


@app.get("/product/{product_id}/")
async def create_user(
        product_id: int, background_tasks: BackgroundTasks
) -> Product:
    background_tasks.add_task(
        write_notification, pk=product_id, message="ИНТЕРЕСНО, ЗАЧЕМ?"
    )
    product = list(
        filter(lambda prod: product_id == prod["product_id"], data)
    )

    if len(product) == 0:
        message = f"Товар с id {product_id} не найден!"
        raise HTTPException(status_code=404, detail=message)
    return Product.parse_obj(product[0])


@app.get("/products/search/")
async def product_search(
        keyword: str, category: str = None, limit: int = 10
) -> list[Product]:
    if category:
        result = list(
            filter(
                lambda prod:
                category.lower() == prod["category"].lower()
                and keyword.lower() in prod["name"].lower().split(), data
            )
        )
        return [Product.parse_obj(product) for product in result][:limit]

    result = list(
        filter(lambda prod: keyword.lower() in prod["name"].lower().split(),
               data)
    )

    return [Product.parse_obj(product) for product in result][:limit]
