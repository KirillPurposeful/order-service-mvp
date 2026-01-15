"""Product entity."""

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class Product:
    """Product entity."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    price: Decimal = Decimal("0")
    stock: int = 0

    def __post_init__(self) -> None:
        """Validate product."""
        if not self.name:
            raise ValueError("Product name cannot be empty")
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if self.stock < 0:
            raise ValueError("Stock cannot be negative")

    def reserve_stock(self, quantity: int) -> None:
        """Reserve stock for order."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.stock < quantity:
            raise ValueError(
                f"Insufficient stock: {self.stock} available, {quantity} requested"
            )
        self.stock -= quantity

    def release_stock(self, quantity: int) -> None:
        """Release reserved stock."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.stock += quantity

