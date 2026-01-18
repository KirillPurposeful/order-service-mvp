"""In-memory repository implementations for MVP."""

from src.core.entities.order import Order
from src.core.entities.product import Product
from src.infrastructure.database.base_repository import BaseRepository


class InMemoryOrderRepository(BaseRepository[Order]):
    """In-memory order repository."""

    pass


class InMemoryProductRepository(BaseRepository[Product]):
    """In-memory product repository."""

    pass

