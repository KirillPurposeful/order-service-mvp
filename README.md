# Order Service - Quick Start

## Run

```bash
python run.py
```

Server starts at `http://localhost:8002`

## API Usage

### Swagger UI (easiest way)

Open: **http://localhost:8002/docs**

### Step 1: Use fixed product IDs

**Products are always available with same IDs:**

```
Laptop   - 550e8400-e29b-41d4-a716-446655440001 ($999.99)
Mouse    - 550e8400-e29b-41d4-a716-446655440002 ($29.99)
Keyboard - 550e8400-e29b-41d4-a716-446655440003 ($89.99)
```

**No need to search for IDs in console!** Just use these IDs above.

### Step 2: Create order

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

**Just click "Try it out" → "Execute" in Swagger!** Example is already filled.

**Response:**
```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "customer_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "items": [...],
  "total": "999.99"
}
```

**Copy order `id`!**

### Step 3: Get order by ID

**GET** `/api/v1/orders/{order_id}`

Paste copied ID instead of `{order_id}`

### Step 4: Get all orders

**GET** `/api/v1/orders/`

### Step 5: Delete order

**DELETE** `/api/v1/orders/{order_id}`

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/orders/` | Create order |
| GET | `/api/v1/orders/` | Get all orders |
| GET | `/api/v1/orders/{id}` | Get order by ID |
| DELETE | `/api/v1/orders/{id}` | Delete order |
| GET | `/health` | Health check |

---

## Architecture

**Clean Architecture** (Onion) - 4 layers:

- `src/core/` - Domain (entities, value objects, exceptions)
- `src/services/` - Application (business logic)
- `src/infrastructure/` - Infrastructure (repositories)
- `src/api/` - Presentation (HTTP endpoints)

**Technologies:**
- FastAPI + Pydantic
- Python 3.12.9 with full typing
- In-memory storage (easy to replace with PostgreSQL)


