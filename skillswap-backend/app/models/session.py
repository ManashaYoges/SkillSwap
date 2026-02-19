from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SessionCreate(BaseModel):
    partner_id: str
    skill: str
    scheduled_time: datetime
    duration_minutes: int = 60

class SessionResponse(BaseModel):
    id: str
    requester_id: str
    partner_id: str
    partner_name: str
    skill: str
    scheduled_time: datetime
    duration_minutes: int
    status: str   # pending / confirmed / completed / cancelled
    coins_earned: Optional[int] = None
    created_at: datetime

class SessionConfirm(BaseModel):
    session_id: str

class LedgerEntry(BaseModel):
    id: str
    user_id: str
    type: str          # earned / spent
    amount: int
    description: str
    session_id: Optional[str] = None
    created_at: datetime
