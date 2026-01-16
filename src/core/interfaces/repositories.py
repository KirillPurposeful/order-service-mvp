"""Repository interfaces."""

from typing import Protocol
from uuid import UUID

from src.core.entities.order import Order
from src.core.entities.product import Product


class OrderRepository(Protocol):
    """Order repository interface."""

    async def save(self, order: Order) -> None:
        """Save order."""
        ...

    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Get order by ID."""
        ...

    async def get_all(self) -> list[Order]:
        """Get all orders."""
        ...

    async def delete(self, order_id: UUID) -> bool:
        """Delete order by ID."""
        ...


class ProductRepository(Protocol):
    """Product repository interface."""

    async def get_by_id(self, product_id: UUID) -> Product | None:
        """Get product by ID."""
        ...

    async def save(self, product: Product) -> None:
        """Save product."""
        ...

