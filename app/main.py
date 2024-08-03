from datetime import datetime

from fastapi import BackgroundTasks, FastAPI, Cookie, Response, Request, HTTPException
from fastapi.responses import JSONResponse

from app.models.models import Product, UserAuth

app = FastAPI(title="my_app", version="v1")

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
    UserAuth(username="vasya", password="31maet"),
    UserAuth(username="masha", password="qwerty")
]


def write_notification(pk: int, message=""):
    with open("log.txt", mode="a+", encoding="utf-8") as email_file:
        print("ФОНОВАЯ ЗАДАЧА")
        res = email_file.read()
        content = f"Искали ID -> {pk}: {message}\n"
        email_file.write(res + content)


@app.post("/login")
async def login(user: UserAuth, response: Response):
    response.delete_cookie(key="session_token")
    search_user = [us for us in users_bd if us.username == user.username]
    if len(search_user) == 0:
        message = f"Пользователь {user.username} не зарегистрирован"
        raise HTTPException(status_code=401, detail=message)

    if user.password == search_user[0].password:
        token = str(user.username + user.password)
        print(token)
        response.set_cookie(key="session_token", value=token, httponly=True)
        content = {"message": "Вход выполнен"}
        return JSONResponse(status_code=200, content=content)
    raise HTTPException(status_code=401, detail="Неверный пароль!")


@app.get("/user")
async def user(request: Request) -> JSONResponse:
    user_token = request.cookies.get("session_token")
    print(user_token)
    for us in users_bd:
        if str(us.username + us.password) == user_token:
            return us

    content = "Пожалуйста авторизуйтесь в системе!"
    raise HTTPException(status_code=401, detail=content)


@app.get("/product/{product_id}")
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


@app.get("/products/search")
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
