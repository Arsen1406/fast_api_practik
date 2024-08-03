from pydantic import BaseModel


class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float


class UserAuth(BaseModel):
    username: str
    password: str
