"""
models/session_model.py
Pydantic schemas for Session documents.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    requester_id: str       # User requesting the session
    provider_id: str        # User who will teach
    skill: str              # Skill being exchanged
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = ""


class SessionOut(BaseModel):
    id: str
    requester_id: str
    provider_id: str
    requester_name: str
    provider_name: str
    skill: str
    status: str             # "pending" | "confirmed" | "completed" | "cancelled"
    coins_spent: int        # Cost deducted from requester
    coins_earned: int       # Reward given to provider
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class SessionConfirm(BaseModel):
    session_id: str
    rating: Optional[int] = None  # 1–5 stars, given by requester on confirm


def session_from_doc(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc