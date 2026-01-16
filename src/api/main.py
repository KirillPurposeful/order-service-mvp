"""FastAPI application."""

from decimal import Decimal
from uuid import uuid4

from fastapi import FastAPI

from src.api.routes import orders
from src.core.entities.product import Product
from src.infrastructure.database.memory_repositories import InMemoryProductRepository

app = FastAPI(
    title="Сервис заказов",
    description="""
## 🛒 Простой сервис для управления заказами

Этот API позволяет создавать заказы и автоматически резервировать товары на складе.

### Что умеет:

* Создавать заказы из нескольких товаров
* Проверять наличие товара на складе
* Считать итоговую стоимость автоматически

### Как попробовать:

**Шаг 1:** При запуске сервера в консоли появятся ID тестовых товаров (Laptop, Mouse, Keyboard)

**Шаг 2:** Скопируйте эти ID

**Шаг 3:** Используйте endpoint ниже ⬇️ и нажмите "Try it out"

**Шаг 4:** Вставьте скопированные ID в запрос и нажмите "Execute"

Готово! 🎉
    """,
    version="0.1.0",
    contact={
        "name": "Order Service Team",
        "url": "https://github.com/yourrepo/order-service",
    },
    license_info={
        "name": "MIT",
    },
)

# Include routers
app.include_router(orders.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize test data on startup."""
    # Get product repository and add some test products
    from src.api.dependencies import get_product_repository

    product_repo = get_product_repository()

    # Add test products
    test_products = [
        Product(
            id=uuid4(),
            name="Laptop",
            description="High-performance laptop",
            price=Decimal("999.99"),
            stock=10,
        ),
        Product(
            id=uuid4(),
            name="Mouse",
            description="Wireless mouse",
            price=Decimal("29.99"),
            stock=50,
        ),
        Product(
            id=uuid4(),
            name="Keyboard",
            description="Mechanical keyboard",
            price=Decimal("89.99"),
            stock=25,
        ),
    ]

    for product in test_products:
        await product_repo.save(product)

    print("✅ Test products initialized")
    print(f"   - {test_products[0].name} (ID: {test_products[0].id})")
    print(f"   - {test_products[1].name} (ID: {test_products[1].id})")
    print(f"   - {test_products[2].name} (ID: {test_products[2].id})")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Order Service MVP",
        "docs": "/docs",
        "api": "/api/v1",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

