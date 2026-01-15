"""FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends

from src.core.interfaces.repositories import OrderRepository, ProductRepository
from src.infrastructure.database.memory_repositories import (
    InMemoryOrderRepository,
    InMemoryProductRepository,
)
from src.services.order_service import OrderService

# Global repositories (in-memory for MVP)
_order_repo = InMemoryOrderRepository()
_product_repo = InMemoryProductRepository()


def get_order_repository() -> OrderRepository:
    """Get order repository."""
    return _order_repo


def get_product_repository() -> ProductRepository:
    """Get product repository."""
    return _product_repo


def get_order_service(
    order_repo: Annotated[OrderRepository, Depends(get_order_repository)],
    product_repo: Annotated[ProductRepository, Depends(get_product_repository)],
) -> OrderService:
    """Get order service."""
    return OrderService(order_repo, product_repo)

