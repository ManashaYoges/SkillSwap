"""
models/transaction_model.py
Pydantic schemas for SkillCoin transactions.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TransactionOut(BaseModel):
    id: str
    user_id: str
    type: str               # "earned" | "spent"
    amount: int             # Positive = earned, negative = spent
    description: str
    session_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


def tx_from_doc(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc