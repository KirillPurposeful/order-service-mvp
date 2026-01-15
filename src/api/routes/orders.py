"""Order routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_order_service
from src.api.schemas.order_schemas import CreateOrderRequest, OrderResponse
from src.core.exceptions import InsufficientStockError, ProductNotFoundError
from src.services.order_service import (
    CreateOrderItemRequest,
    CreateOrderRequest as ServiceCreateOrderRequest,
    OrderService,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заказ",
    response_description="Заказ успешно создан",
    responses={
        201: {
            "description": "Заказ создан успешно",
            "content": {
                "application/json": {
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
                            }
                        ],
                        "total": "999.99"
                    }
                }
            }
        },
        400: {
            "description": "Недостаточно товара на складе",
            "content": {
                "application/json": {
                    "example": {"detail": "Insufficient stock: 10 available, 999 requested"}
                }
            }
        },
        404: {
            "description": "Продукт не найден",
            "content": {
                "application/json": {
                    "example": {"detail": "Product 00000000-0000-0000-0000-000000000000 not found"}
                }
            }
        },
        422: {
            "description": "Ошибка валидации данных",
        }
    }
)
async def create_order(
    request: CreateOrderRequest,
    order_service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    """
    Создать новый заказ с автоматическим резервированием товара.

    **Процесс создания заказа:**

    1. Проверка наличия всех продуктов
    2. Резервирование товара на складе
    3. Создание заказа со статусом PENDING
    4. Расчет общей стоимости

    **Параметры:**

    - **customer_id**: UUID покупателя
    - **items**: Список товаров для заказа
        - **product_id**: UUID продукта (получите из логов сервера при старте)
        - **quantity**: Количество товара (должно быть > 0)

    **Пример запроса:**
    ```json
    {
      "customer_id": "550e8400-e29b-41d4-a716-446655440000",
      "items": [
        {
          "product_id": "ЗАМЕНИТЕ_НА_РЕАЛЬНЫЙ_ID",
          "quantity": 1
        }
      ]
    }
    ```

    **Возможные ошибки:**

    - `404` - Продукт не найден
    - `400` - Недостаточно товара на складе
    - `422` - Невалидные данные (отрицательное количество, пустой список и т.д.)
    """
    try:
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

