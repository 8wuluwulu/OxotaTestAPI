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