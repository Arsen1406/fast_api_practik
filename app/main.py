from fastapi import FastAPI

from app.models.models import Product

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


@app.get("/product/{product_id}")
async def create_user(product_id: int) -> Product | dict[str, str]:
    product = list(
        filter(lambda prod: product_id == prod["product_id"], data)
    )

    if len(product) == 0:
        return {"message": f"Товар с id {product_id} не найден!"}
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
        filter(lambda prod: keyword.lower() in prod["name"].lower().split(), data)
    )

    return [Product.parse_obj(product) for product in result][:limit]
