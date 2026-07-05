import uuid
import asyncio
import json
from datetime import datetime
from src.database import async_engine, async_session
from src.models import Base, LeadModel, OutboxEventModel, InboundEventsModel
from fastapi import FastAPI, HTTPException, status
from sqlalchemy import select
from fastapi.responses import JSONResponse
from src.schemas import LeadCreateSchema, LeadResponseSchema

app = FastAPI()

@app.get("/leads/{lead_id}", response_model=LeadResponseSchema)
async def get_lead(lead_id: uuid.UUID):
    async with async_session() as session:
        async with session.begin():
            stmt = select(LeadModel).where(LeadModel.id == lead_id)
            lead = await session.scalar(stmt)

            if lead is None:
                correlation_id = str(uuid.uuid4())
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        "error": {
                            "code": "lead_not_found",
                            "message": "Заявка не найдена",
                            "correlation_id": correlation_id
                        }
                    }
                )

    return lead

@app.post("/leads", response_model=LeadResponseSchema)
async def create_lead(lead: LeadCreateSchema):
    lead_id = uuid.uuid4()

    async with async_session() as session:
        async with session.begin():
            new_lead = LeadModel(
                id=lead_id,
                name=lead.name,
                phone=lead.phone,
                source=lead.source,
                comment=lead.comment
            )
            session.add(new_lead)

            kafka_payload = {
                "lead_id": str(lead_id),
                "name": lead.name,
                "phone": lead.phone,
                "source": lead.source
            }

            outbox_event = OutboxEventModel(
                event_id=uuid.uuid4(),
                event_type="lead_created.v1",
                aggregate_id=str(lead_id),
                occurred_at=datetime.now(),
                payload=kafka_payload
            )
            session.add(outbox_event)

    return new_lead