import asyncio
import json
import uuid
from aiokafka import AIOKafkaConsumer
from sqlalchemy import select
from src.database import async_session
from src.models import LeadModel, LeadStatus, InboundEventsModel

KAFKA_SERVERS = "localhost:9092"
KAFKA_TOPIC = "lead_moderation.events.v1"

async def consume_events():
    consumer = AIOKafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_SERVERS, group_id="leads-group")
    await consumer.start()
    print("все норм")
    try:
        async for msg in consumer:
            event_data = json.loads(msg.value.decode("utf-8"))
            print(f"Получили событие {event_data}")

            event_id = uuid.UUID(event_data["event_id"])
            event_type = event_data["event_type"]
            lead_id = uuid.UUID(event_data["aggregate_id"])
            approved = event_data["payload"]["approved"]

            async with async_session() as session:
                async with session.begin():
                    query = select(InboundEventsModel).where(InboundEventsModel.id == event_id)
                    result = await session.execute(query)
                    event = result.scalar()
                    if event is not None:
                        print(f"событие {event_id} - дубликат ")
                        continue

                    new_event = InboundEventsModel(
                        id=event_id,
                        event_type=event_type
                    )
                    session.add(new_event)

                    lead_query = select(LeadModel).where(LeadModel.id == lead_id)
                    lead_result = await session.execute(lead_query)
                    lead = lead_result.scalar()

                    if lead is not None:
                        if approved == True:
                            lead.status = LeadStatus.approved
                        else:
                            lead.status = LeadStatus.rejected
                        print(f"Обновили статус лида {lead_id} на {lead.status}")
                    else:
                        print(f"Лид {lead_id} не найден")


    finally:
        await consumer.stop()
        print("consumer остановлен")

if __name__ == "__main__":
    asyncio.run(consume_events())


