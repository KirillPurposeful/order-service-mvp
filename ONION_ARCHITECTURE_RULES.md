# Архитектурные правила для нового проекта (Луковая архитектура)

---

## 🎯 Принципы архитектуры

### Луковая архитектура (Onion Architecture)

**Слои** (от центра к краям):
1. **Core** (Domain) — бизнес-логика, независима от внешнего мира
2. **Services** (Application) — оркестрация бизнес-операций
3. **Infrastructure** — интеграция с внешним миром (БД, API)
4. **API** — точка входа (HTTP endpoints)

**Правило зависимостей**:
```
API → Services → Core
Infrastructure → Services → Core

Core НЕ ЗАВИСИТ НИ ОТ КОГО
```

---

## 📁 Структура проекта

```
project/
├── src/
│   ├── core/                    # Domain layer (ядро)
│   │   ├── entities/           # Бизнес-сущности с логикой
│   │   │   ├── order.py
│   │   │   └── product.py
│   │   ├── value_objects/      # Неизменяемые значения
│   │   │   └── money.py
│   │   ├── interfaces/         # Контракты (Protocols)
│   │   │   └── repositories.py
│   │   └── exceptions.py       # Бизнес-исключения
│   │
│   ├── services/               # Application layer
│   │   ├── order_service.py   # Бизнес-операции Order
│   │   └── product_service.py
│   │
│   ├── infrastructure/         # Внешний мир
│   │   ├── database/
│   │   │   ├── models.py      # SQLAlchemy модели
│   │   │   ├── repositories.py # Реализация репозиториев
│   │   │   └── migrations/    # Alembic
│   │   ├── redis/
│   │   │   └── cache.py
│   │   └── external/
│   │       └── binance_client.py
│   │
│   ├── api/                    # Presentation layer
│   │   ├── routes/
│   │   │   ├── orders.py      # FastAPI routes для Order
│   │   │   └── products.py
│   │   ├── schemas/           # Pydantic Request/Response
│   │   │   └── order_schemas.py
│   │   ├── dependencies.py    # FastAPI Depends
│   │   └── main.py           # FastAPI app
│   │
│   ├── config.py              # Pydantic Settings
│   └── __init__.py
│
├── tests/
│   ├── unit/
│   │   ├── core/
│   │   └── services/
│   ├── integration/
│   │   └── api/
│   └── conftest.py
│
├── alembic/
├── .env.example
├── pyproject.toml
├── docker-compose.yml
└── README.md
```

---

## 🏗️ Правила слоев

### 1. Core Layer (Domain)

**Что содержит**:
- Entities — сущности с бизнес-логикой
- Value Objects — неизменяемые значения
- Protocols — контракты для зависимостей
- Exceptions — бизнес-ошибки

**Правила**:
- ❌ НЕ зависит от FastAPI, SQLAlchemy, Redis, внешних API
- ❌ НЕ содержит async/await (если бизнес-логика синхронная)
- ✅ Только чистая Python бизнес-логика
- ✅ 100% покрытие type hints
- ✅ Immutable где возможно (`@dataclass(frozen=True)`)

**Пример Entity**:
```python
# src/core/entities/order.py
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from decimal import Decimal

@dataclass
class Order:
    """Order entity with business logic."""
    
    id: UUID = field(default_factory=uuid4)
    customer_id: UUID
    items: list['OrderItem'] = field(default_factory=list)
    status: str = "PENDING"
    
    def add_item(self, product_id: UUID, quantity: int, price: Decimal) -> None:
        """Add item with validation (business rule)."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        self.items.append(OrderItem(
            product_id=product_id,
            quantity=quantity,
            price=price
        ))
    
    def calculate_total(self) -> Decimal:
        """Calculate order total."""
        return sum(item.subtotal for item in self.items)
    
    def confirm(self) -> None:
        """Confirm order (business rule)."""
        if not self.items:
            raise ValueError("Cannot confirm empty order")
        if self.status != "PENDING":
            raise ValueError("Order already processed")
        
        self.status = "CONFIRMED"


@dataclass
class OrderItem:
    product_id: UUID
    quantity: int
    price: Decimal
    
    @property
    def subtotal(self) -> Decimal:
        return self.price * self.quantity
```

**Пример Value Object**:
```python
# src/core/value_objects/money.py
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class Money:
    """Money value object."""
    
    amount: Decimal
    currency: str
    
    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3 characters (ISO 4217)")
        
        # Force uppercase
        object.__setattr__(self, 'currency', self.currency.upper())
    
    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __mul__(self, multiplier: int | Decimal) -> 'Money':
        return Money(self.amount * Decimal(multiplier), self.currency)
```

**Пример Protocol (интерфейс)**:
```python
# src/core/interfaces/repositories.py
from typing import Protocol
from uuid import UUID
from core.entities.order import Order

class OrderRepository(Protocol):
    """Order repository interface (Dependency Inversion)."""
    
    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Get order by ID."""
        ...
    
    async def save(self, order: Order) -> None:
        """Save order."""
        ...
    
    async def delete(self, order_id: UUID) -> None:
        """Delete order."""
        ...
```

**Пример Exceptions**:
```python
# src/core/exceptions.py

class DomainError(Exception):
    """Base domain error."""

class OrderNotFoundError(DomainError):
    """Order not found."""

class InvalidOrderStateError(DomainError):
    """Invalid order state transition."""

class ProductNotFoundError(DomainError):
    """Product not found."""
```

---

### 2. Services Layer (Application)

**Что содержит**:
- Бизнес-операции (use cases)
- Оркестрация entities и repositories
- Транзакционная логика

**Правила**:
- ✅ Зависит от Core (entities, protocols, exceptions)
- ✅ Использует async/await
- ✅ Принимает зависимости через конструктор (DI)
- ❌ НЕ знает про FastAPI, Pydantic schemas, HTTP
- ❌ НЕ создает зависимости сам (только через DI)

**Пример Service**:
```python
# src/services/order_service.py
from uuid import UUID
from decimal import Decimal
from typing import Protocol

from core.entities.order import Order, OrderItem
from core.interfaces.repositories import OrderRepository, ProductRepository
from core.exceptions import ProductNotFoundError

# Request DTO (простой dataclass, НЕ Pydantic)
from dataclasses import dataclass

@dataclass
class CreateOrderRequest:
    customer_id: UUID
    items: list['CreateOrderItemRequest']

@dataclass
class CreateOrderItemRequest:
    product_id: UUID
    quantity: int


class OrderService:
    """Order business operations."""
    
    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
    ):
        self._order_repo = order_repo
        self._product_repo = product_repo
    
    async def create_order(self, request: CreateOrderRequest) -> Order:
        """Create new order."""
        # Создаем entity
        order = Order(customer_id=request.customer_id)
        
        # Бизнес-логика: добавление items с валидацией
        for item_req in request.items:
            product = await self._product_repo.get_by_id(item_req.product_id)
            if not product:
                raise ProductNotFoundError(f"Product {item_req.product_id} not found")
            
            # Используем domain метод
            order.add_item(
                product_id=product.id,
                quantity=item_req.quantity,
                price=product.price
            )
        
        # Сохраняем
        await self._order_repo.save(order)
        
        return order
    
    async def confirm_order(self, order_id: UUID) -> Order:
        """Confirm order."""
        order = await self._order_repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")
        
        # Используем domain метод
        order.confirm()
        
        await self._order_repo.save(order)
        
        return order
```

---

### 3. Infrastructure Layer

**Что содержит**:
- Реализация репозиториев (SQLAlchemy)
- Database модели (ORM)
- Внешние API клиенты
- Redis, RabbitMQ и т.д.

**Правила**:
- ✅ Зависит от Core (protocols, entities)
- ✅ Реализует интерфейсы из Core
- ✅ Содержит технические детали (SQL, HTTP)
- ❌ НЕ содержит бизнес-логику

**Пример Database Models**:
```python
# src/infrastructure/database/models.py
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid import UUID
from decimal import Decimal
from datetime import datetime

class Base(DeclarativeBase):
    pass

class OrderModel(Base):
    __tablename__ = "orders"
    
    id: Mapped[UUID] = mapped_column(primary_key=True)
    customer_id: Mapped[UUID] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    items: Mapped[list["OrderItemModel"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )

class OrderItemModel(Base):
    __tablename__ = "order_items"
    
    id: Mapped[UUID] = mapped_column(primary_key=True)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[UUID]
    quantity: Mapped[int]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    # Relationships
    order: Mapped["OrderModel"] = relationship(back_populates="items")
```

**Пример Repository Implementation**:
```python
# src/infrastructure/database/repositories.py
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.entities.order import Order, OrderItem
from core.interfaces.repositories import OrderRepository
from infrastructure.database.models import OrderModel, OrderItemModel


class SQLAlchemyOrderRepository:
    """SQLAlchemy implementation of OrderRepository."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Get order by ID."""
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        result = await self._session.execute(stmt)
        db_order = result.scalar_one_or_none()
        
        if not db_order:
            return None
        
        # Маппинг DB → Domain (простой, без отдельного Mapper класса)
        return Order(
            id=db_order.id,
            customer_id=db_order.customer_id,
            status=db_order.status,
            items=[
                OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.price
                )
                for item in db_order.items
            ]
        )
    
    async def save(self, order: Order) -> None:
        """Save order."""
        # Проверяем существование
        stmt = select(OrderModel).where(OrderModel.id == order.id)
        result = await self._session.execute(stmt)
        db_order = result.scalar_one_or_none()
        
        if db_order:
            # Update
            db_order.status = order.status
            # Обновить items (упрощенно — удалить и создать заново)
            db_order.items.clear()
        else:
            # Create
            db_order = OrderModel(
                id=order.id,
                customer_id=order.customer_id,
                status=order.status
            )
            self._session.add(db_order)
        
        # Добавить items
        for item in order.items:
            db_order.items.append(
                OrderItemModel(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.price
                )
            )
        
        await self._session.flush()
    
    async def delete(self, order_id: UUID) -> None:
        """Delete order."""
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        result = await self._session.execute(stmt)
        db_order = result.scalar_one_or_none()
        
        if db_order:
            await self._session.delete(db_order)
            await self._session.flush()
```

---

### 4. API Layer (FastAPI)

**Что содержит**:
- HTTP routes
- Pydantic Request/Response schemas
- Dependencies (DI)
- Error handlers

**Правила**:
- ✅ Зависит от Services и Core
- ✅ Использует Pydantic для валидации
- ✅ Тонкий слой (только HTTP ↔ Service)
- ❌ НЕ содержит бизнес-логику

**Пример Pydantic Schemas**:
```python
# src/api/schemas/order_schemas.py
from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from datetime import datetime

class OrderItemRequest(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0, description="Quantity must be positive")

class CreateOrderRequest(BaseModel):
    customer_id: UUID
    items: list[OrderItemRequest] = Field(min_length=1)

class OrderItemResponse(BaseModel):
    product_id: UUID
    quantity: int
    price: Decimal
    subtotal: Decimal

class OrderResponse(BaseModel):
    id: UUID
    customer_id: UUID
    status: str
    items: list[OrderItemResponse]
    total: Decimal
    created_at: datetime
    
    @classmethod
    def from_entity(cls, order: Order) -> 'OrderResponse':
        """Convert domain entity to response."""
        return cls(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.price,
                    subtotal=item.subtotal
                )
                for item in order.items
            ],
            total=order.calculate_total(),
            created_at=datetime.utcnow()  # Упрощенно
        )
```

**Пример Dependencies (FastAPI DI)**:
```python
# src/api/dependencies.py
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from infrastructure.database.repositories import (
    SQLAlchemyOrderRepository,
    SQLAlchemyProductRepository
)
from services.order_service import OrderService
from config import settings

# Database
engine = create_async_engine(settings.database_url, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncIterator[AsyncSession]:
    """Get database session."""
    async with async_session_maker() as session:
        yield session

async def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    """Get order service with dependencies."""
    order_repo = SQLAlchemyOrderRepository(db)
    product_repo = SQLAlchemyProductRepository(db)
    return OrderService(order_repo, product_repo)
```

**Пример Routes**:
```python
# src/api/routes/orders.py
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from api.schemas.order_schemas import CreateOrderRequest, OrderResponse
from api.dependencies import get_order_service
from services.order_service import OrderService, CreateOrderRequest as ServiceRequest
from core.exceptions import OrderNotFoundError, ProductNotFoundError

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new order",
    description="Creates a new order for the specified customer",
    responses={
        201: {"description": "Order created successfully"},
        400: {"description": "Invalid request or business rule violation"},
        404: {"description": "Product not found"},
    }
)
async def create_order(
    request: CreateOrderRequest,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Create new order endpoint."""
    try:
        # Конвертируем Pydantic → Service DTO
        service_request = ServiceRequest(
            customer_id=request.customer_id,
            items=[
                CreateOrderItemRequest(
                    product_id=item.product_id,
                    quantity=item.quantity
                )
                for item in request.items
            ]
        )
        
        # Вызываем service
        order = await service.create_order(service_request)
        
        # Конвертируем Entity → Pydantic
        return OrderResponse.from_entity(order)
    
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{order_id}/confirm",
    response_model=OrderResponse,
    summary="Confirm order",
    responses={
        200: {"description": "Order confirmed"},
        404: {"description": "Order not found"},
        400: {"description": "Invalid order state"},
    }
)
async def confirm_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Confirm order endpoint."""
    try:
        order = await service.confirm_order(order_id)
        return OrderResponse.from_entity(order)
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Пример FastAPI App**:
```python
# src/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import orders, products
from core.exceptions import DomainError
from fastapi import Request
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Order Management API",
    description="Clean Architecture example with Onion pattern",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(orders.router, prefix="/api")
app.include_router(products.router, prefix="/api")

# Exception handlers
@app.exception_handler(DomainError)
async def domain_exception_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=400,
        content={"error": exc.__class__.__name__, "message": str(exc)}
    )

@app.get("/health")
async def health():
    return {"status": "ok"}
```

---

## 🧪 Testing

**Правила**:
- ✅ Unit тесты для Core (entities, value objects) — без моков
- ✅ Unit тесты для Services — с моками репозиториев
- ✅ Integration тесты для API — с test database

**Пример Unit Test (Core)**:
```python
# tests/unit/core/test_order.py
import pytest
from uuid import uuid4
from decimal import Decimal

from core.entities.order import Order

def test_add_item_success():
    """Test adding item to order."""
    order = Order(customer_id=uuid4())
    
    order.add_item(
        product_id=uuid4(),
        quantity=2,
        price=Decimal("10.00")
    )
    
    assert len(order.items) == 1
    assert order.items[0].quantity == 2

def test_add_item_invalid_quantity():
    """Test adding item with invalid quantity raises error."""
    order = Order(customer_id=uuid4())
    
    with pytest.raises(ValueError, match="Quantity must be positive"):
        order.add_item(
            product_id=uuid4(),
            quantity=0,
            price=Decimal("10.00")
        )

def test_confirm_empty_order_raises():
    """Test confirming empty order raises error."""
    order = Order(customer_id=uuid4())
    
    with pytest.raises(ValueError, match="Cannot confirm empty order"):
        order.confirm()
```

**Пример Unit Test (Service)**:
```python
# tests/unit/services/test_order_service.py
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from decimal import Decimal

from services.order_service import OrderService, CreateOrderRequest, CreateOrderItemRequest
from core.entities.order import Order
from core.entities.product import Product
from core.exceptions import ProductNotFoundError

@pytest.fixture
def order_repo():
    return AsyncMock()

@pytest.fixture
def product_repo():
    return AsyncMock()

@pytest.fixture
def order_service(order_repo, product_repo):
    return OrderService(order_repo, product_repo)

async def test_create_order_success(order_service, product_repo, order_repo):
    """Test successful order creation."""
    # Given
    customer_id = uuid4()
    product_id = uuid4()
    product = Product(id=product_id, name="Test", price=Decimal("10.00"))
    product_repo.get_by_id.return_value = product
    
    request = CreateOrderRequest(
        customer_id=customer_id,
        items=[CreateOrderItemRequest(product_id=product_id, quantity=2)]
    )
    
    # When
    order = await order_service.create_order(request)
    
    # Then
    assert order.customer_id == customer_id
    assert len(order.items) == 1
    order_repo.save.assert_called_once()

async def test_create_order_product_not_found(order_service, product_repo):
    """Test order creation with non-existent product."""
    # Given
    product_repo.get_by_id.return_value = None
    request = CreateOrderRequest(
        customer_id=uuid4(),
        items=[CreateOrderItemRequest(product_id=uuid4(), quantity=1)]
    )
    
    # When/Then
    with pytest.raises(ProductNotFoundError):
        await order_service.create_order(request)
```

---

## ⚙️ Configuration

**Pydantic Settings**:
```python
# src/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Security
    secret_key: str
    
    # Logging
    log_level: str = "INFO"

settings = Settings()
```

---

## 📦 Dependencies (pyproject.toml)

```toml
[tool.poetry]
name = "order-service"
version = "0.1.0"
description = "Order management service with Clean Architecture"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.36"}
asyncpg = "^0.30.0"
alembic = "^1.14.0"
pydantic = "^2.10.3"
pydantic-settings = "^2.7.0"
redis = {extras = ["hiredis"], version = "^5.2.0"}

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.4"
pytest-asyncio = "^0.24.0"
pytest-cov = "^6.0.0"
httpx = "^0.28.1"
mypy = "^1.13.0"
ruff = "^0.8.4"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

## 🐳 Docker

**docker-compose.yml**:
```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@db:5432/orders
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./src:/app/src

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: orders
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## 📚 Финальная проверка

### ✅ Архитектура правильная, если:

1. **Core не зависит от внешнего мира**
   ```python
   # ✅ Правильно
   class Order:  # Нет import FastAPI, SQLAlchemy
       def confirm(self): ...
   
   # ❌ Неправильно
   from fastapi import HTTPException  # Core зависит от FastAPI
   ```

2. **Services зависят только от Core**
   ```python
   # ✅ Правильно
   class OrderService:
       def __init__(self, repo: OrderRepository):  # Protocol из Core
           ...
   
   # ❌ Неправильно
   class OrderService:
       def __init__(self, db: AsyncSession):  # Зависит от SQLAlchemy
           ...
   ```

3. **API — тонкий слой**
   ```python
   # ✅ Правильно (только HTTP ↔ Service)
   @router.post("/orders")
   async def create_order(req: CreateOrderRequest, svc: OrderService = Depends(...)):
       order = await svc.create_order(req)
       return OrderResponse.from_entity(order)
   
   # ❌ Неправильно (бизнес-логика в API)
   @router.post("/orders")
   async def create_order(req: CreateOrderRequest, db: AsyncSession = Depends(...)):
       order = Order(...)  # Создаем entity в API
       order.add_item(...)  # Бизнес-логика в API
       db.add(order)  # Работаем с DB напрямую
   ```

4. **Тесты изолированы**
   ```python
   # ✅ Unit test (Service)
   async def test_create_order(order_service, product_repo_mock):
       product_repo_mock.get_by_id.return_value = Product(...)
       order = await order_service.create_order(...)
       assert order.status == "PENDING"
   
   # ✅ Integration test (API)
   async def test_create_order_endpoint(client: AsyncClient):
       response = await client.post("/orders", json={...})
       assert response.status_code == 201
   ```

---

**Этот подход позволит создать чистый, масштабируемый проект для портфолио, демонстрирующий знание ООП, SOLID и Clean Architecture без over-engineering.**

