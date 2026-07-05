import asyncio
import json
import logging
from sqlalchemy import select
from aiokafka import AIOKafkaProducer
from src.database import async_session
from src.models import OutboxEventModel

KAFKA_SERVERS = "localhost:9092"
KAFKA_TOPIC = "leads.events.v1"

async def public_events():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_SERVERS)
    await producer.start()
    print("Всё норм")

    try:
        while True:
            async with async_session() as session:
                async with session.begin():
                    query = select(OutboxEventModel).where(OutboxEventModel.is_published == False)
                    result = await session.execute(query)
                    events = result.scalars().all()

                    if len(events) > 0:
                        print(f"Неотправленных: {len(events)}")
                        for event in events:
                            message = {
                                "event_id": str(event.event_id),
                                "event_type": event.event_type,
                                "aggregate_id": event.aggregate_id,
                                "occurred_at": event.occurred_at.isoformat() + "Z",
                                "payload": event.payload
                            }

                            value_bytes = json.dumps(message).encode("utf-8")

                            await producer.send_and_wait(
                                KAFKA_TOPIC,
                                value=value_bytes,
                                key=event.aggregate_id.encode("utf-8")
                            )
                            print("Отправили")

                            event.is_published = True

            await asyncio.sleep(1)

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await producer.stop()
        print(f"Воркер остановлен")

if __name__ == "__main__":
    asyncio.run(public_events())

