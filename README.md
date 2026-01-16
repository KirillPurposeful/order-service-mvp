# Order Service - Quick Start

## Запуск

```bash
python run.py
```

Сервер запустится на `http://localhost:8002`

## Использование API

### Swagger UI (самый простой способ)

Откройте: **http://localhost:8002/docs**

### Шаг 1: Используйте фиксированные ID товаров

**Товары всегда доступны с одинаковыми ID:**

```
Laptop   - 550e8400-e29b-41d4-a716-446655440001 (999.99₽)
Mouse    - 550e8400-e29b-41d4-a716-446655440002 (29.99₽)
Keyboard - 550e8400-e29b-41d4-a716-446655440003 (89.99₽)
```

**Не нужно искать ID в консоли!** Просто используйте эти ⬆️

### Шаг 2: Создайте заказ

**POST** `/api/v1/orders/`

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

**Просто нажмите "Try it out" → "Execute" в Swagger!** Пример уже заполнен ✨

**Ответ:**
```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "customer_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "items": [...],
  "total": "999.99"
}
```

**Скопируйте `id` заказа!**

### Шаг 3: Получите заказ по ID

**GET** `/api/v1/orders/{order_id}`

Вставьте скопированный ID вместо `{order_id}`

### Шаг 4: Список всех заказов

**GET** `/api/v1/orders/`

### Шаг 5: Удалить заказ

**DELETE** `/api/v1/orders/{order_id}`

---

## Endpoints

| Method | Path | Описание |
|--------|------|----------|
| POST | `/api/v1/orders/` | Создать заказ |
| GET | `/api/v1/orders/` | Список всех заказов |
| GET | `/api/v1/orders/{id}` | Получить заказ по ID |
| DELETE | `/api/v1/orders/{id}` | Удалить заказ |
| GET | `/health` | Health check |

---

## Архитектура

**Clean Architecture** (Onion) - 4 слоя:

- `src/core/` - Domain (entities, value objects, exceptions)
- `src/services/` - Application (business logic)
- `src/infrastructure/` - Infrastructure (repositories)
- `src/api/` - Presentation (HTTP endpoints)

**Технологии:**
- FastAPI + Pydantic
- Python 3.11+ с полной типизацией
- In-memory storage (легко заменить на PostgreSQL)

