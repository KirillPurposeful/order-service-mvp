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
    summary="Создать заказ",
    response_description="Заказ успешно создан",
    responses={
        201: {
            "description": "✅ Заказ создан, товар зарезервирован",
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
            "description": "❌ Товара не хватает на складе",
            "content": {
                "application/json": {
                    "example": {"detail": "Insufficient stock: 10 available, 999 requested"}
                }
            }
        },
        404: {
            "description": "❌ Такого товара не существует",
            "content": {
                "application/json": {
                    "example": {"detail": "Product 00000000-0000-0000-0000-000000000000 not found"}
                }
            }
        },
        422: {
            "description": "❌ Некорректные данные в запросе",
        }
    }
)
async def create_order(
    request: CreateOrderRequest,
    order_service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    """
    Создать заказ из списка товаров.

    Система автоматически:
    - Проверит наличие товара
    - Зарезервирует его на складе
    - Посчитает общую сумму

    ### Доступные товары (фиксированные ID):

    - **Laptop** - `550e8400-e29b-41d4-a716-446655440001` (999.99₽, в наличии: 10)
    - **Mouse** - `550e8400-e29b-41d4-a716-446655440002` (29.99₽, в наличии: 50)
    - **Keyboard** - `550e8400-e29b-41d4-a716-446655440003` (89.99₽, в наличии: 25)

    ### Пример запроса:

    Используйте ID выше ⬆️ - они всегда одинаковые!

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

    Просто нажмите **"Try it out"** и **"Execute"** - пример уже готов! ✨
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
    summary="Список всех заказов",
    description="Получить все созданные заказы",
)
async def get_all_orders(
    order_service: Annotated[OrderService, Depends(get_order_service)],
) -> list[OrderResponse]:
    """
    Получить список всех заказов.

    Возвращает все заказы, созданные в системе.
    """
    orders = await order_service.get_all_orders()
    return [OrderResponse.from_entity(order) for order in orders]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Найти заказ по ID",
    description="Получить заказ по его уникальному идентификатору",
    responses={
        404: {
            "description": "❌ Заказ не найден",
            "content": {
                "application/json": {
                    "example": {"detail": "Заказ не найден"}
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
    Получить заказ по ID.

    Введите ID заказа из списка или созданного ранее заказа.
    """
    order = await order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    return OrderResponse.from_entity(order)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить заказ",
    description="Удалить заказ из системы",
    responses={
        204: {"description": "✅ Заказ успешно удален"},
        404: {
            "description": "❌ Заказ не найден",
            "content": {
                "application/json": {
                    "example": {"detail": "Заказ не найден"}
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
    Удалить заказ по ID.

    Заказ будет полностью удален из системы.
    """
    success = await order_service.cancel_order(order_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )

