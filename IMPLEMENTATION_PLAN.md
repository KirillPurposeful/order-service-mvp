# Implementation Plan — Луковая архитектура с FastAPI

---

## 🎯 Цель

Создать портфолио проект, демонстрирующий:
- ✅ Знание ООП (инкапсуляция, наследование, полиморфизм)
- ✅ SOLID принципы
- ✅ Луковую архитектуру (Clean Architecture)
- ✅ Type hints 100%
- ✅ Тестирование (unit + integration)
- ✅ Async/await с FastAPI
- ✅ Docker + PostgreSQL + Redis

---

## 📅 План реализации (10 дней)

---

## **Этап 1: Настройка проекта (День 1)**

### Задачи:

#### 1.1 Создать структуру директорий
```bash
mkdir -p order-service/{src/{core/{entities,value_objects,interfaces},services,infrastructure/{database,redis,external},api/{routes,schemas}},tests/{unit/{core,services},integration/api},alembic/versions}

cd order-service

# Создать __init__.py
touch src/__init__.py
touch src/core/__init__.py
touch src/core/entities/__init__.py
touch src/core/value_objects/__init__.py
touch src/core/interfaces/__init__.py
touch src/services/__init__.py
touch src/infrastructure/__init__.py
touch src/infrastructure/database/__init__.py
touch src/api/__init__.py
touch src/api/routes/__init__.py
touch src/api/schemas/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
```

#### 1.2 Инициализировать Poetry
```bash
poetry init --name order-service --description "Order management with Clean Architecture"

# Добавить зависимости
poetry add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic pydantic pydantic-settings redis[hiredis]

# Dev dependencies
poetry add --group dev pytest pytest-asyncio pytest-cov httpx mypy ruff pre-commit
```

#### 1.3 Создать .env.example
```bash
cat > .env.example << 'EOF'
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/orders

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secret-key-change-in-production

# Logging
LOG_LEVEL=INFO
EOF

cp .env.example .env
```

#### 1.4 Создать pyproject.toml конфигурацию
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
pre-commit = "^4.0.1"

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
addopts = "--cov=src --cov-report=html --cov-report=term"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

#### 1.5 Инициализировать Alembic
```bash
alembic init alembic

# Отредактировать alembic.ini
# sqlalchemy.url = postgresql+asyncpg://user:password@localhost:5432/orders
```

#### 1.6 Создать docker-compose.yml
```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@db:5432/orders
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: dev-secret-key
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./src:/app/src
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

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
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d orders"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  postgres_data:
```

#### 1.7 Создать Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy dependencies
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy source
COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 1.8 Создать .gitignore
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/

# Env
.env
.env.local

# Database
*.db
*.sqlite3

# Alembic
alembic/versions/*.pyc
```

### ✅ Чеклист День 1:
- [ ] Структура директорий создана
- [ ] Poetry настроен, зависимости установлены
- [ ] .env и docker-compose.yml готовы
- [ ] Git репозиторий инициализирован
- [ ] `docker-compose up db redis` запускается

---

## **Этап 2: Core Layer — Domain (День 2-3)**

### Задачи:

#### 2.1 Создать exceptions (src/core/exceptions.py)
```python
"""Domain exceptions."""


class DomainError(Exception):
    """Base domain error."""


class OrderNotFoundError(DomainError):
    """Order not found."""


class ProductNotFoundError(DomainError):
    """Product not found."""


class InvalidOrderStateError(DomainError):
    """Invalid order state transition."""


class InsufficientStockError(DomainError):
    """Insufficient product stock."""
```

#### 2.2 Создать Money value object (src/core/value_objects/money.py)
```python
"""Money value object."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Money:
    """Money value object."""

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        """Validate money."""
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3 characters (ISO 4217)")
        if not self.currency.isupper():
            raise ValueError("Currency must be uppercase")

    def __add__(self, other: "Money") -> "Money":
        """Add two money values."""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        """Subtract money."""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, multiplier: int | Decimal) -> "Money":
        """Multiply money by number."""
        return Money(self.amount * Decimal(multiplier), self.currency)

    def __lt__(self, other: "Money") -> bool:
        """Less than comparison."""
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        """Less than or equal comparison."""
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        """Greater than comparison."""
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        """Greater than or equal comparison."""
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount >= other.amount
```

#### 2.3 Создать Product entity (src/core/entities/product.py)
```python
"""Product entity."""

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class Product:
    """Product entity."""

    id: UUID = field(default_factory=uuid4)
    name: str
    description: str
    price: Decimal
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
            raise ValueError(f"Insufficient stock: {self.stock} available, {quantity} requested")
        
        self.stock -= quantity

    def release_stock(self, quantity: int) -> None:
        """Release reserved stock."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        self.stock += quantity
```

#### 2.4 Создать Order entity (src/core/entities/order.py)
```python
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
    customer_id: UUID
    items: list[OrderItem] = field(default_factory=list)
    status: str = "PENDING"

    def add_item(self, product_id: UUID, product_name: str, quantity: int, price: Decimal) -> None:
        """Add item to order with validation."""
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

    def complete(self) -> None:
        """Mark order as completed."""
        if self.status != "CONFIRMED":
            raise ValueError("Can only complete confirmed orders")

        self.status = "COMPLETED"
```

#### 2.5 Создать repository protocols (src/core/interfaces/repositories.py)
```python
"""Repository interfaces (Dependency Inversion Principle)."""

from typing import Protocol
from uuid import UUID

from src.core.entities.order import Order
from src.core.entities.product import Product


class OrderRepository(Protocol):
    """Order repository interface."""

    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Get order by ID."""
        ...

    async def save(self, order: Order) -> None:
        """Save order."""
        ...

    async def delete(self, order_id: UUID) -> None:
        """Delete order."""
        ...

    async def list_by_customer(self, customer_id: UUID) -> list[Order]:
        """List orders by customer."""
        ...


class ProductRepository(Protocol):
    """Product repository interface."""

    async def get_by_id(self, product_id: UUID) -> Product | None:
        """Get product by ID."""
        ...

    async def save(self, product: Product) -> None:
        """Save product."""
        ...

    async def list_all(self) -> list[Product]:
        """List all products."""
        ...
```

#### 2.6 Написать unit тесты для entities

**tests/unit/core/test_money.py**:
```python
"""Tests for Money value object."""

import pytest
from decimal import Decimal

from src.core.value_objects.money import Money


def test_money_creation_valid():
    """Test valid money creation."""
    money = Money(Decimal("100.00"), "USD")
    assert money.amount == Decimal("100.00")
    assert money.currency == "USD"


def test_money_negative_amount_raises():
    """Test negative amount raises error."""
    with pytest.raises(ValueError, match="cannot be negative"):
        Money(Decimal("-10.00"), "USD")


def test_money_invalid_currency_length():
    """Test invalid currency length raises error."""
    with pytest.raises(ValueError, match="3 characters"):
        Money(Decimal("100.00"), "US")


def test_money_lowercase_currency_raises():
    """Test lowercase currency raises error."""
    with pytest.raises(ValueError, match="uppercase"):
        Money(Decimal("100.00"), "usd")


def test_money_addition():
    """Test adding two money values."""
    m1 = Money(Decimal("100.00"), "USD")
    m2 = Money(Decimal("50.00"), "USD")
    result = m1 + m2
    
    assert result.amount == Decimal("150.00")
    assert result.currency == "USD"


def test_money_addition_different_currencies_raises():
    """Test adding different currencies raises error."""
    m1 = Money(Decimal("100.00"), "USD")
    m2 = Money(Decimal("50.00"), "EUR")
    
    with pytest.raises(ValueError, match="different currencies"):
        m1 + m2


def test_money_multiplication():
    """Test multiplying money."""
    money = Money(Decimal("10.00"), "USD")
    result = money * 3
    
    assert result.amount == Decimal("30.00")
    assert result.currency == "USD"
```

**tests/unit/core/test_order.py**:
```python
"""Tests for Order entity."""

import pytest
from uuid import uuid4
from decimal import Decimal

from src.core.entities.order import Order


def test_order_creation():
    """Test order creation."""
    order = Order(customer_id=uuid4())
    
    assert order.status == "PENDING"
    assert len(order.items) == 0


def test_add_item_success():
    """Test adding item to order."""
    order = Order(customer_id=uuid4())
    
    order.add_item(
        product_id=uuid4(),
        product_name="Test Product",
        quantity=2,
        price=Decimal("10.00")
    )
    
    assert len(order.items) == 1
    assert order.items[0].quantity == 2
    assert order.items[0].subtotal == Decimal("20.00")


def test_add_item_invalid_quantity_raises():
    """Test adding item with invalid quantity raises error."""
    order = Order(customer_id=uuid4())
    
    with pytest.raises(ValueError, match="Quantity must be positive"):
        order.add_item(
            product_id=uuid4(),
            product_name="Test",
            quantity=0,
            price=Decimal("10.00")
        )


def test_calculate_total():
    """Test calculating order total."""
    order = Order(customer_id=uuid4())
    order.add_item(uuid4(), "Product 1", 2, Decimal("10.00"))
    order.add_item(uuid4(), "Product 2", 1, Decimal("15.00"))
    
    total = order.calculate_total()
    assert total == Decimal("35.00")


def test_confirm_order_success():
    """Test confirming order."""
    order = Order(customer_id=uuid4())
    order.add_item(uuid4(), "Product", 1, Decimal("10.00"))
    
    order.confirm()
    assert order.status == "CONFIRMED"


def test_confirm_empty_order_raises():
    """Test confirming empty order raises error."""
    order = Order(customer_id=uuid4())
    
    with pytest.raises(ValueError, match="Cannot confirm empty order"):
        order.confirm()


def test_cancel_order():
    """Test cancelling order."""
    order = Order(customer_id=uuid4())
    order.add_item(uuid4(), "Product", 1, Decimal("10.00"))
    
    order.cancel()
    assert order.status == "CANCELLED"
```

### ✅ Чеклист День 2-3:
- [ ] Все entities созданы с бизнес-логикой
- [ ] Value objects immutable (frozen=True)
- [ ] Repository protocols определены
- [ ] Unit тесты для entities написаны
- [ ] Все тесты проходят: `pytest tests/unit/core/`
- [ ] mypy --strict проходит

---

## **Этап 3: Infrastructure Layer (День 4-5)**

### Задачи:

#### 3.1 Создать database models (src/infrastructure/database/models.py)
```python
"""SQLAlchemy database models."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Numeric, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""


class ProductModel(Base):
    """Product database model."""

    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class OrderModel(Base):
    """Order database model."""

    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    # Relationships
    items: Mapped[list["OrderItemModel"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItemModel(Base):
    """Order item database model."""

    __tablename__ = "order_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[UUID]
    product_name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # Relationships
    order: Mapped["OrderModel"] = relationship(back_populates="items")
```

#### 3.2 Создать Alembic миграции
```bash
# Настроить alembic/env.py для async
# Создать первую миграцию
alembic revision --autogenerate -m "Initial tables"
alembic upgrade head
```

#### 3.3 Создать database session (src/infrastructure/database/session.py)
```python
"""Database session management."""

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

# Create async engine
engine = create_async_engine(settings.database_url, echo=settings.log_level == "DEBUG")

# Create session maker
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Get database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

#### 3.4 Создать repositories (src/infrastructure/database/repositories.py)
```python
"""Repository implementations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.entities.order import Order, OrderItem
from src.core.entities.product import Product
from src.infrastructure.database.models import OrderItemModel, OrderModel, ProductModel


class SQLAlchemyProductRepository:
    """SQLAlchemy implementation of ProductRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, product_id: UUID) -> Product | None:
        """Get product by ID."""
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        result = await self._session.execute(stmt)
        db_product = result.scalar_one_or_none()

        if not db_product:
            return None

        return Product(
            id=db_product.id,
            name=db_product.name,
            description=db_product.description,
            price=db_product.price,
            stock=db_product.stock,
        )

    async def save(self, product: Product) -> None:
        """Save product."""
        stmt = select(ProductModel).where(ProductModel.id == product.id)
        result = await self._session.execute(stmt)
        db_product = result.scalar_one_or_none()

        if db_product:
            # Update
            db_product.name = product.name
            db_product.description = product.description
            db_product.price = product.price
            db_product.stock = product.stock
        else:
            # Create
            db_product = ProductModel(
                id=product.id,
                name=product.name,
                description=product.description,
                price=product.price,
                stock=product.stock,
            )
            self._session.add(db_product)

        await self._session.flush()

    async def list_all(self) -> list[Product]:
        """List all products."""
        stmt = select(ProductModel)
        result = await self._session.execute(stmt)
        db_products = result.scalars().all()

        return [
            Product(
                id=p.id,
                name=p.name,
                description=p.description,
                price=p.price,
                stock=p.stock,
            )
            for p in db_products
        ]


class SQLAlchemyOrderRepository:
    """SQLAlchemy implementation of OrderRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Get order by ID."""
        stmt = select(OrderModel).where(OrderModel.id == order_id).options(selectinload(OrderModel.items))
        result = await self._session.execute(stmt)
        db_order = result.scalar_one_or_none()

        if not db_order:
            return None

        return Order(
            id=db_order.id,
            customer_id=db_order.customer_id,
            status=db_order.status,
            items=[
                OrderItem(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    price=item.price,
                )
                for item in db_order.items
            ],
        )

    async def save(self, order: Order) -> None:
        """Save order."""
        stmt = select(OrderModel).where(OrderModel.id == order.id).options(selectinload(OrderModel.items))
        result = await self._session.execute(stmt)
        db_order = result.scalar_one_or_none()

        if db_order:
            # Update existing
            db_order.status = order.status
            db_order.items.clear()
        else:
            # Create new
            db_order = OrderModel(
                id=order.id,
                customer_id=order.customer_id,
                status=order.status,
            )
            self._session.add(db_order)

        # Add items
        for item in order.items:
            db_order.items.append(
                OrderItemModel(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    price=item.price,
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

    async def list_by_customer(self, customer_id: UUID) -> list[Order]:
        """List orders by customer."""
        stmt = (
            select(OrderModel)
            .where(OrderModel.customer_id == customer_id)
            .options(selectinload(OrderModel.items))
        )
        result = await self._session.execute(stmt)
        db_orders = result.scalars().all()

        return [
            Order(
                id=order.id,
                customer_id=order.customer_id,
                status=order.status,
                items=[
                    OrderItem(
                        product_id=item.product_id,
                        product_name=item.product_name,
                        quantity=item.quantity,
                        price=item.price,
                    )
                    for item in order.items
                ],
            )
            for order in db_orders
        ]
```

#### 3.5 Создать config (src/config.py)
```python
"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

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

### ✅ Чеклист День 4-5:
- [ ] SQLAlchemy модели созданы
- [ ] Alembic миграции созданы и применены
- [ ] Repositories реализованы
- [ ] Database session настроен
- [ ] Можно запустить PostgreSQL и применить миграции

---

## **Этап 4: Services Layer (День 6-7)**

### Задачи:

#### 4.1 Создать Order Service (src/services/order_service.py)

```python
"""Order business operations."""

from dataclasses import dataclass
from uuid import UUID

from src.core.entities.order import Order
from src.core.exceptions import OrderNotFoundError, ProductNotFoundError, InsufficientStockError
from src.core.interfaces.repositories import OrderRepository, ProductRepository


@dataclass
class CreateOrderItemRequest:
    """Create order item request."""

    product_id: UUID
    quantity: int


@dataclass
class CreateOrderRequest:
    """Create order request."""

    customer_id: UUID
    items: list[CreateOrderItemRequest]


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
        """Create new order with stock reservation."""
        # Create order entity
        order = Order(customer_id=request.customer_id)

        # Add items and reserve stock
        for item_req in request.items:
            product = await self._product_repo.get_by_id(item_req.product_id)
            if not product:
                raise ProductNotFoundError(f"Product {item_req.product_id} not found")

            # Reserve stock (business logic in Product entity)
            try:
                product.reserve_stock(item_req.quantity)
            except ValueError as e:
                raise InsufficientStockError(str(e))

            # Add item to order
            order.add_item(
                product_id=product.id,
                product_name=product.name,
                quantity=item_req.quantity,
                price=product.price,
            )

            # Save updated product stock
            await self._product_repo.save(product)

        # Save order
        await self._order_repo.save(order)

        return order

    async def confirm_order(self, order_id: UUID) -> Order:
        """Confirm order."""
        order = await self._order_repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")

        # Use domain method
        order.confirm()

        await self._order_repo.save(order)

        return order

    async def cancel_order(self, order_id: UUID) -> Order:
        """Cancel order and release stock."""
        order = await self._order_repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")

        # Release stock for each item
        for item in order.items:
            product = await self._product_repo.get_by_id(item.product_id)
            if product:
                product.release_stock(item.quantity)
                await self._product_repo.save(product)

        # Cancel order
        order.cancel()
        await self._order_repo.save(order)

        return order

    async def get_order(self, order_id: UUID) -> Order:
        """Get order by ID."""
        order = await self._order_repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")
        return order

    async def list_customer_orders(self, customer_id: UUID) -> list[Order]:
        """List customer orders."""
        return await self._order_repo.list_by_customer(customer_id)
```

#### 4.2 Создать Product Service (src/services/product_service.py)

```python
"""Product business operations."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.core.entities.product import Product
from src.core.exceptions import ProductNotFoundError
from src.core.interfaces.repositories import ProductRepository


@dataclass
class CreateProductRequest:
    """Create product request."""

    name: str
    description: str
    price: Decimal
    stock: int = 0


class ProductService:
    """Product business operations."""

    def __init__(self, product_repo: ProductRepository):
        self._product_repo = product_repo

    async def create_product(self, request: CreateProductRequest) -> Product:
        """Create new product."""
        product = Product(
            name=request.name,
            description=request.description,
            price=request.price,
            stock=request.stock,
        )

        await self._product_repo.save(product)

        return product

    async def get_product(self, product_id: UUID) -> Product:
        """Get product by ID."""
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")
        return product

    async def list_products(self) -> list[Product]:
        """List all products."""
        return await self._product_repo.list_all()

    async def update_stock(self, product_id: UUID, quantity: int) -> Product:
        """Update product stock."""
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")

        product.stock = quantity
        await self._product_repo.save(product)

        return product
```

#### 4.3 Написать unit тесты для services

**tests/unit/services/test_order_service.py**:
```python
"""Tests for OrderService."""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from src.core.entities.order import Order
from src.core.entities.product import Product
from src.core.exceptions import OrderNotFoundError, ProductNotFoundError
from src.services.order_service import CreateOrderItemRequest, CreateOrderRequest, OrderService


@pytest.fixture
def order_repo():
    """Mock order repository."""
    return AsyncMock()


@pytest.fixture
def product_repo():
    """Mock product repository."""
    return AsyncMock()


@pytest.fixture
def order_service(order_repo, product_repo):
    """Order service instance."""
    return OrderService(order_repo, product_repo)


@pytest.mark.asyncio
async def test_create_order_success(order_service, product_repo, order_repo):
    """Test successful order creation."""
    # Given
    customer_id = uuid4()
    product_id = uuid4()
    product = Product(
        id=product_id, name="Test Product", description="Test", price=Decimal("10.00"), stock=10
    )
    product_repo.get_by_id.return_value = product

    request = CreateOrderRequest(
        customer_id=customer_id, items=[CreateOrderItemRequest(product_id=product_id, quantity=2)]
    )

    # When
    order = await order_service.create_order(request)

    # Then
    assert order.customer_id == customer_id
    assert len(order.items) == 1
    assert order.items[0].quantity == 2
    assert product.stock == 8  # Stock reserved
    order_repo.save.assert_called_once()
    product_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_create_order_product_not_found(order_service, product_repo):
    """Test order creation with non-existent product."""
    # Given
    product_repo.get_by_id.return_value = None
    request = CreateOrderRequest(
        customer_id=uuid4(), items=[CreateOrderItemRequest(product_id=uuid4(), quantity=1)]
    )

    # When/Then
    with pytest.raises(ProductNotFoundError):
        await order_service.create_order(request)


@pytest.mark.asyncio
async def test_confirm_order_success(order_service, order_repo):
    """Test confirming order."""
    # Given
    order_id = uuid4()
    order = Order(id=order_id, customer_id=uuid4())
    order.add_item(uuid4(), "Product", 1, Decimal("10.00"))
    order_repo.get_by_id.return_value = order

    # When
    result = await order_service.confirm_order(order_id)

    # Then
    assert result.status == "CONFIRMED"
    order_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_confirm_order_not_found(order_service, order_repo):
    """Test confirming non-existent order."""
    # Given
    order_repo.get_by_id.return_value = None

    # When/Then
    with pytest.raises(OrderNotFoundError):
        await order_service.confirm_order(uuid4())
```

### ✅ Чеклист День 6-7:
- [ ] OrderService реализован
- [ ] ProductService реализован
- [ ] Services не зависят от FastAPI/Pydantic
- [ ] Unit тесты с моками написаны
- [ ] Все тесты проходят: `pytest tests/unit/services/`
- [ ] Покрытие > 80%

---

## **Этап 5: API Layer (День 8-9)**

### Задачи:

#### 5.1 Создать Pydantic schemas (src/api/schemas/order_schemas.py)

```python
"""Order API schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.entities.order import Order


class OrderItemRequest(BaseModel):
    """Order item request."""

    product_id: UUID
    quantity: int = Field(gt=0, description="Quantity must be positive")


class CreateOrderRequest(BaseModel):
    """Create order request."""

    customer_id: UUID
    items: list[OrderItemRequest] = Field(min_length=1, description="At least one item required")


class OrderItemResponse(BaseModel):
    """Order item response."""

    product_id: UUID
    product_name: str
    quantity: int
    price: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    """Order response."""

    id: UUID
    customer_id: UUID
    status: str
    items: list[OrderItemResponse]
    total: Decimal
    created_at: datetime

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
            created_at=datetime.utcnow(),  # Simplified
        )
```

(Продолжить с product_schemas, dependencies, routes...)

Из-за ограничения длины, полный план сохранен в файл. Продолжение следует...

### ✅ Чеклист День 8-9:
- [ ] Pydantic schemas созданы
- [ ] FastAPI dependencies настроены
- [ ] Routes реализованы
- [ ] Error handlers добавлены
- [ ] Swagger документация полная
- [ ] Integration тесты написаны

---

## **Этап 6: Финализация (День 10)**

### Задачи:
1. ✅ Настроить структурированное логирование
2. ✅ Создать README.md с примерами
3. ✅ Проверить Docker Compose
4. ✅ Настроить CI/CD (GitHub Actions)
5. ✅ Проверить покрытие тестами > 80%
6. ✅ Запустить mypy --strict
7. ✅ Отформатировать код (ruff format)

### ✅ Финальный чеклист:
- [ ] `docker-compose up` запускает весь стек
- [ ] README содержит curl примеры
- [ ] Все тесты проходят (unit + integration)
- [ ] Покрытие > 80%
- [ ] mypy --strict без ошибок
- [ ] Swagger доступен на /api/docs
- [ ] GitHub Actions CI проходит

---

## 🎯 Результат

После 10 дней получаем:
- ✅ Чистую луковую архитектуру
- ✅ ООП с инкапсуляцией бизнес-логики
- ✅ SOLID принципы (особенно DIP)
- ✅ 100% type hints
- ✅ >80% test coverage
- ✅ Production-ready Docker setup
- ✅ Отличную Swagger документацию

**Готовый портфолио проект для демонстрации навыков!**

