"""Тестовый скрипт для проверки API."""
import asyncio
import httpx


async def test_api():
    """Тест всех endpoints."""
    base_url = "http://localhost:8002"

    async with httpx.AsyncClient() as client:
        print("🔍 1. Проверка health...")
        response = await client.get(f"{base_url}/health")
        print(f"   ✅ {response.json()}")

        print("\n📋 2. Получение списка заказов (должен быть пустой)...")
        response = await client.get(f"{base_url}/api/v1/orders/")
        orders = response.json()
        print(f"   ✅ Заказов: {len(orders)}")

        print("\n🛒 3. Создание тестового заказа...")
        print("   ⚠️  Замените product_id на реальный из консоли при запуске сервера!")
        create_data = {
            "customer_id": "550e8400-e29b-41d4-a716-446655440000",
            "items": [
                {
                    "product_id": "ЗАМЕНИТЕ_МЕНЯ",  # Вставьте ID из консоли
                    "quantity": 1
                }
            ]
        }
        print(f"   Данные: {create_data}")
        # response = await client.post(f"{base_url}/api/v1/orders/", json=create_data)
        # order = response.json()
        # print(f"   ✅ Создан: {order['id']}")

        print("\n💡 Инструкция:")
        print("   1. Запустите сервер: python run.py")
        print("   2. Скопируйте ID товара из консоли")
        print("   3. Откройте Swagger: http://localhost:8002/docs")
        print("   4. POST /api/v1/orders/ → вставьте ID → Execute")
        print("   5. Скопируйте ID созданного заказа")
        print("   6. GET /api/v1/orders/{order_id} → вставьте ID → Execute")


if __name__ == "__main__":
    asyncio.run(test_api())

