# Order Service MVP - Clean Architecture

Сервис заказов с луковой архитектурой (Onion Architecture).

## Особенности

- ✅ Луковая архитектура - 4 независимых слоя (Core, Service, Infrastructure, API)
- ✅ SOLID принципы - Dependency Inversion через Protocol
- ✅ 100% Type Hints
- ✅ FastAPI + Pydantic v2
- ✅ **Swagger UI** - интерактивная документация API (см. [SWAGGER.md](SWAGGER.md))
- ✅ In-memory repositories (легко заменить на PostgreSQL)

## Структура

```
src/
├── core/              # Domain Layer (ядро)
│   ├── entities/      # Order, Product
│   ├── interfaces/    # Repository Protocols
│   └── exceptions.py
├── services/          # Service Layer
│   └── order_service.py
├── infrastructure/    # Infrastructure Layer
│   └── database/
│       └── memory_repositories.py
└── api/              # API Layer
    ├── routes/       # HTTP endpoints
    ├── schemas/      # Pydantic models
    └── main.py       # FastAPI app
```

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск сервера

```bash
python run.py
```

Сервер запустится на `http://localhost:8000`

### 3. Документация API (Swagger UI)

Откройте в браузере: **`http://localhost:8002/docs`**

**Swagger UI включает:**

- 📝 Интерактивная документация всех endpoints
- 🎯 Примеры запросов и ответов
- ▶️ Возможность тестировать API прямо в браузере
- 📊 Схемы данных (Pydantic models)
- ❌ Примеры ошибок (404, 400, 422)

**Также доступно:**
- ReDoc: `http://localhost:8002/redoc` - альтернативная документация
- OpenAPI JSON: `http://localhost:8002/openapi.json` - схема в формате OpenAPI 3.0

## Использование

### Создать заказ

При старте сервера создаются тестовые продукты. Их ID выводятся в консоль:

```
✅ Test products initialized
   - Laptop (ID: 123e4567-...)
   - Mouse (ID: 234e5678-...)
```

Создайте заказ через Swagger UI или curl:

```bash
curl -X POST "http://localhost:8000/api/v1/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "items": [
      {
        "product_id": "ЗАМЕНИТЕ_НА_ID_LAPTOP",
        "quantity": 1
      }
    ]
  }'
```

## Архитектура

### Луковая архитектура

```
API Layer → Service Layer → Core Layer ← Infrastructure Layer
                              ↑
                         Все зависят от Core
                         Core не зависит ни от кого!
```

### SOLID принципы

- **S** - Single Responsibility: каждый класс имеет одну обязанность
- **O** - Open/Closed: легко добавить новый Repository
- **L** - Liskov Substitution: любой Repository взаимозаменяем
- **I** - Interface Segregation: OrderRepo и ProductRepo разделены
- **D** - Dependency Inversion: Service зависит от Protocol ⭐

## Следующие шаги

См. [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) для полного плана развития:

- Добавить PostgreSQL + SQLAlchemy
- Unit и Integration тесты
- Docker Compose
- Больше endpoints (GET, PUT, DELETE)
- JWT authentication

