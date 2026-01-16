"""Order API schemas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from src.core.entities.order import Order


class OrderItemRequest(BaseModel):
    """Товар в заказе."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "123e4567-e89b-12d3-a456-426614174000",
                "quantity": 2
            }
        }
    )

    product_id: UUID = Field(description="ID товара (скопируйте из консоли)")
    quantity: int = Field(gt=0, description="Сколько штук (минимум 1)")


class CreateOrderRequest(BaseModel):
    """Запрос на создание заказа."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_id": "550e8400-e29b-41d4-a716-446655440000",
                "items": [
                    {
                        "product_id": "123e4567-e89b-12d3-a456-426614174000",
                        "quantity": 1
                    },
                    {
                        "product_id": "234e5678-e89b-12d3-a456-426614174001",
                        "quantity": 2
                    }
                ]
            }
        }
    )

    customer_id: UUID = Field(description="ID покупателя (можете использовать из примера)")
    items: list[OrderItemRequest] = Field(
        min_length=1,
        description="Список товаров (минимум 1)"
    )


class OrderItemResponse(BaseModel):
    """Order item response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "123e4567-e89b-12d3-a456-426614174000",
                "product_name": "Laptop",
                "quantity": 1,
                "price": "999.99",
                "subtotal": "999.99"
            }
        }
    )

    product_id: UUID
    product_name: str
    quantity: int
    price: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    """Order response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "customer_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "PENDING",
                "items": [
                    {
                        "product_id": "123e4567-e89b-12d3-a456-426614174000",
                        "product_name": "Laptop",
                        "quantity": 1,
                        "price": "999.99",
                        "subtotal": "999.99"
                    },
                    {
                        "product_id": "234e5678-e89b-12d3-a456-426614174001",
                        "product_name": "Mouse",
                        "quantity": 2,
                        "price": "29.99",
                        "subtotal": "59.98"
                    }
                ],
                "total": "1059.97"
            }
        }
    )

    id: UUID
    customer_id: UUID
    status: str
    items: list[OrderItemResponse]
    total: Decimal

    @classmethod
    def from_entity(cls, order: Order) -> "OrderResponse":
        """Convert domain entity to response."""
        return cls(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    price=item.price,
                    subtotal=item.subtotal,
                )
                for item in order.items
            ],
            total=order.calculate_total(),
        )

