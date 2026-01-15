"""Domain exceptions."""


class DomainError(Exception):
    """Base domain error."""


class OrderNotFoundError(DomainError):
    """Order not found."""


class ProductNotFoundError(DomainError):
    """Product not found."""


class InsufficientStockError(DomainError):
    """Insufficient product stock."""

