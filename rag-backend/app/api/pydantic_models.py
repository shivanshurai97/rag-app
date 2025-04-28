from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import List
import uuid

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: uuid.UUID
    username: str

    class Config:
        from_attributes = True

class DocumentSelectionRequest(BaseModel):
    session_id: str
    document_ids: List[uuid.UUID]

class DocumentOut(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    enabled_for_qa: bool

    class Config:
        from_attributes = True

class QARequest(BaseModel):
    question: str

class QAResponse(BaseModel):
    answer: str 