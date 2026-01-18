"""FastAPI application."""

from contextlib import asynccontextmanager
from decimal import Decimal
from uuid import UUID

from fastapi import FastAPI

from src.api.routes import orders
from src.core.entities.product import Product

# Fixed product IDs for consistent Swagger examples
LAPTOP_ID = UUID("550e8400-e29b-41d4-a716-446655440001")
MOUSE_ID = UUID("550e8400-e29b-41d4-a716-446655440002")
KEYBOARD_ID = UUID("550e8400-e29b-41d4-a716-446655440003")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Initialize test data
    from src.api.dependencies import get_product_repository

    product_repo = get_product_repository()

    # Add test products with fixed IDs
    test_products = [
        Product(
            id=LAPTOP_ID,
            name="Laptop",
            description="High-performance laptop",
            price=Decimal("999.99"),
            stock=10,
        ),
        Product(
            id=MOUSE_ID,
            name="Mouse",
            description="Wireless mouse",
            price=Decimal("29.99"),
            stock=50,
        ),
        Product(
            id=KEYBOARD_ID,
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

    yield

    # Shutdown: cleanup if needed
    print("👋 Application shutdown")


app = FastAPI(
    title="Order Service",
    description="""
## 🛒 Simple Order Management Service

This API allows you to create orders and automatically reserve products in stock.

### Features:

* Create orders with multiple products
* Automatic stock availability check
* Auto-calculate total price

### How to try:

**Step 1:** Products are available with fixed IDs (see below)

**Step 2:** Use endpoint below ⬇️ and click "Try it out"

**Step 3:** Click "Execute"

Done! 🎉
    """,
    version="0.1.0",
    contact={
        "name": "Order Service Team",
        "url": "https://github.com/yourrepo/order-service",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
)

# Include routers
app.include_router(orders.router, prefix="/api/v1")


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

