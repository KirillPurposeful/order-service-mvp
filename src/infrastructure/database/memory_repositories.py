"""In-memory repository implementations for MVP."""

from uuid import UUID

from src.core.entities.order import Order
from src.core.entities.product import Product


class InMemoryOrderRepository:
    """In-memory order repository."""

    def __init__(self) -> None:
        self._orders: dict[UUID, Order] = {}

    async def save(self, order: Order) -> None:
        """Save order."""
        self._orders[order.id] = order

    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Get order by ID."""
        return self._orders.get(order_id)


class InMemoryProductRepository:
    """In-memory product repository."""

    def __init__(self) -> None:
        self._products: dict[UUID, Product] = {}

    async def get_by_id(self, product_id: UUID) -> Product | None:
        """Get product by ID."""
        return self._products.get(product_id)

    async def save(self, product: Product) -> None:
        """Save product."""
        self._products[product.id] = product

