"""Order entity."""

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class OrderItem:
    """Order item."""

    product_id: UUID
    product_name: str
    quantity: int
    price: Decimal

    def __post_init__(self) -> None:
        """Validate order item."""
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.price < 0:
            raise ValueError("Price cannot be negative")

    @property
    def subtotal(self) -> Decimal:
        """Calculate item subtotal."""
        return self.price * self.quantity


@dataclass
class Order:
    """Order entity with business logic."""

    id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default_factory=uuid4)
    items: list[OrderItem] = field(default_factory=list)
    status: str = "PENDING"

    def add_item(
        self, product_id: UUID, product_name: str, quantity: int, price: Decimal
    ) -> None:
        """Add item to order."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price < 0:
            raise ValueError("Price cannot be negative")

        self.items.append(
            OrderItem(
                product_id=product_id,
                product_name=product_name,
                quantity=quantity,
                price=price,
            )
        )

    def calculate_total(self) -> Decimal:
        """Calculate order total."""
        return sum(item.subtotal for item in self.items)

    def confirm(self) -> None:
        """Confirm order (business rule)."""
        if not self.items:
            raise ValueError("Cannot confirm empty order")
        if self.status != "PENDING":
            raise ValueError(f"Cannot confirm order with status {self.status}")
        self.status = "CONFIRMED"

    def cancel(self) -> None:
        """Cancel order."""
        if self.status == "DELIVERED":
            raise ValueError("Cannot cancel delivered order")
        if self.status == "CANCELLED":
            raise ValueError("Order already cancelled")
        self.status = "CANCELLED"

