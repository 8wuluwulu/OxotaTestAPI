import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional
from models import LeadStatus

class LeadCreateSchema(BaseModel):
    name: str
    phone: str
    source: str
    comment: Optional[str] = None

class LeadResponseSchema(BaseModel):
    id: uuid.UUID
    name: str
    phone: str
    source: str
    comment: Optional[str]
    status: LeadStatus

    model_config = ConfigDict(from_attributes=True)

class ErrorDetails(BaseModel):
    code: str
    message: str
    correlation_id: str

class ErrorResponseSchema(BaseModel):
    error: ErrorDetails
