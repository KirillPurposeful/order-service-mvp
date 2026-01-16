"""Order status enum."""

from enum import Enum


class OrderStatus(str, Enum):
    """Order status."""

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    DELIVERED = "DELIVERED"

