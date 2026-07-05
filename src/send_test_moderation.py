import asyncio
import json
import uuid
from datetime import datetime
from aiokafka import AIOKafkaProducer

async def send_test_event():
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()
    
    print("--- Утилита отправки тестового события модерации в Kafka ---")
    lead_id_str = input("Введите UUID лида из базы данных: ").strip()
    try:
        lead_id = uuid.UUID(lead_id_str)
    except ValueError:
        print("Ошибка: Введен некорректный UUID!")
        await producer.stop()
        return
        
    approved_input = input("Одобрить лид? (y - да, n - нет): ").strip().lower()
    approved = approved_input == 'y'
    
    # Генерируем уникальный ID для события модерации
    event_id = uuid.uuid4()
    
    # Формируем структуру события строго по требованиям ТЗ (пункт 4)
    event_payload = {
        "event_id": str(event_id),
        "event_type": "lead_moderation_finished.v1",
        "aggregate_id": str(lead_id),
        "occurred_at": datetime.now().isoformat() + "Z",
        "payload": {
            "lead_id": str(lead_id),
            "approved": approved,
            "reason": None if approved else "Не прошел проверку"
        }
    }
    
    value_bytes = json.dumps(event_payload).encode("utf-8")
    
    # Отправляем в топик, который слушает наш консьюмер
    await producer.send_and_wait("lead_moderation.events.v1", value=value_bytes)
    print(f"\nУспешно отправлено событие в Kafka!")
    print(f"event_id: {event_id}")
    print(f"lead_id: {lead_id}")
    print(f"approved: {approved}")
    
    await producer.stop()

if __name__ == "__main__":
    asyncio.run(send_test_event())
