"""Order business operations."""

from uuid import UUID

from src.core.entities.order import Order
from src.core.exceptions import InsufficientStockError, ProductNotFoundError
from src.core.interfaces.repositories import OrderRepository, ProductRepository


class OrderService:
    """Order business operations."""

    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
    ):
        self._order_repo = order_repo
        self._product_repo = product_repo

    async def create_order(
        self, customer_id: UUID, items: list[tuple[UUID, int]]
    ) -> Order:
        """Create new order with stock reservation.

        Args:
            customer_id: Customer UUID
            items: List of (product_id, quantity) tuples

        Returns:
            Created order entity

        Raises:
            ProductNotFoundError: Product does not exist
            InsufficientStockError: Not enough stock
        """
        # Create order entity
        order = Order(customer_id=customer_id)

        # Add items and reserve stock
        for product_id, quantity in items:
            product = await self._product_repo.get_by_id(product_id)
            if not product:
                raise ProductNotFoundError(f"Product {product_id} not found")

            # Reserve stock (business logic in Product entity)
            try:
                product.reserve_stock(quantity)
            except ValueError as e:
                raise InsufficientStockError(str(e)) from e

            # Add item to order
            order.add_item(
                product_id=product.id,
                product_name=product.name,
                quantity=quantity,
                price=product.price,
            )

            # Save updated product stock
            await self._product_repo.save(product)

        # Save order
        await self._order_repo.save(order)

        return order

    async def get_all_orders(self) -> list[Order]:
        """Get all orders."""
        return await self._order_repo.get_all()

    async def get_order_by_id(self, order_id: UUID) -> Order | None:
        """Get order by ID."""
        return await self._order_repo.get_by_id(order_id)

    async def cancel_order(self, order_id: UUID) -> bool:
        """Cancel order."""
        return await self._order_repo.delete(order_id)

