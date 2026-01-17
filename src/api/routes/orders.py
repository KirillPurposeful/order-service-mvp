"""Order routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_order_service
from src.api.schemas.order_schemas import CreateOrderRequest, OrderResponse
from src.core.exceptions import InsufficientStockError, ProductNotFoundError
from src.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create order",
    response_description="Order successfully created",
    responses={
        201: {
            "description": "✅ Order created, stock reserved",
            "content": {
                "application/json": {
                    "example": {
                        "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                        "customer_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "PENDING",
                        "items": [
                            {
                                "product_id": "550e8400-e29b-41d4-a716-446655440001",
                                "product_name": "Laptop",
                                "quantity": 1,
                                "price": "999.99",
                                "subtotal": "999.99"
                            }
                        ],
                        "total": "999.99"
                    }
                }
            }
        },
        400: {
            "description": "❌ Not enough stock",
            "content": {
                "application/json": {
                    "example": {"detail": "Insufficient stock: 10 available, 999 requested"}
                }
            }
        },
        404: {
            "description": "❌ Product not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Product 00000000-0000-0000-0000-000000000000 not found"}
                }
            }
        },
        422: {
            "description": "❌ Invalid request data",
        }
    }
)
async def create_order(
    request: CreateOrderRequest,
    order_service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    """
    Create order from products list.

    System automatically:
    - Checks product availability
    - Reserves stock
    - Calculates total price

    ### Available products (fixed IDs):

    - **Laptop** - `550e8400-e29b-41d4-a716-446655440001` ($999.99, stock: 10)
    - **Mouse** - `550e8400-e29b-41d4-a716-446655440002` ($29.99, stock: 50)
    - **Keyboard** - `550e8400-e29b-41d4-a716-446655440003` ($89.99, stock: 25)

    ### Example request:

    Use IDs above ⬆️ - they're always the same!

    ```json
    {
      "customer_id": "550e8400-e29b-41d4-a716-446655440000",
      "items": [
        {
          "product_id": "550e8400-e29b-41d4-a716-446655440001",
          "quantity": 1
        }
      ]
    }
    ```

    Just click **"Try it out"** and **"Execute"** - example is ready! ✨
    """
    try:
        # Import service DTOs only here (late binding)
        from src.services.order_service import (
            CreateOrderItemRequest,
            CreateOrderRequest as ServiceCreateOrderRequest,
        )

        # Convert API request to service request
        service_request = ServiceCreateOrderRequest(
            customer_id=request.customer_id,
            items=[
                CreateOrderItemRequest(
                    product_id=item.product_id,
                    quantity=item.quantity,
                )
                for item in request.items
            ],
        )

        order = await order_service.create_order(service_request)
        return OrderResponse.from_entity(order)

    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    except InsufficientStockError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/",
    response_model=list[OrderResponse],
    summary="Get all orders",
    description="Get all created orders",
)
async def get_all_orders(
    order_service: Annotated[OrderService, Depends(get_order_service)],
) -> list[OrderResponse]:
    """
    Get list of all orders.

    Returns all orders created in the system.
    """
    orders = await order_service.get_all_orders()
    return [OrderResponse.from_entity(order) for order in orders]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Find order by ID",
    description="Get order by unique identifier",
    responses={
        404: {
            "description": "❌ Order not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
async def get_order(
    order_id: UUID,
    order_service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    """
    Get order by ID.

    Enter order ID from list or previously created order.
    """
    order = await order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return OrderResponse.from_entity(order)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete order",
    description="Delete order from system",
    responses={
        204: {"description": "✅ Order successfully deleted"},
        404: {
            "description": "❌ Order not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
async def delete_order(
    order_id: UUID,
    order_service: Annotated[OrderService, Depends(get_order_service)],
) -> None:
    """
    Delete order by ID.

    Order will be completely removed from the system.
    """
    success = await order_service.cancel_order(order_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )


@router.get(
    "/demo",
    response_model=OrderResponse,
    summary="🎬 Demo order",
    description="Show example of complete order (doesn't create real order)",
    tags=["demo"]
)
async def get_demo_order() -> OrderResponse:
    """
    Get demonstration order.

    **Just click Execute!** You'll immediately see what real API response looks like.

    This does NOT create actual order, just shows response format.
    """
    from decimal import Decimal
    from src.core.entities.order import Order, OrderItem
    from uuid import UUID

    # Create demo order
    demo_order = Order(
        id=UUID("7c9e6679-7425-40de-944b-e07fc1f90ae7"),
        customer_id=UUID("550e8400-e29b-41d4-a716-446655440000")
    )

    demo_order.add_item(
        product_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
        product_name="Laptop",
        quantity=1,
        price=Decimal("999.99")
    )

    demo_order.add_item(
        product_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
        product_name="Mouse",
        quantity=2,
        price=Decimal("29.99")
    )

    return OrderResponse.from_entity(demo_order)
