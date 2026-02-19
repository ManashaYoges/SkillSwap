"""
models/user_model.py
Pydantic schemas for User documents.
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


class SkillEntry(BaseModel):
    """Single skill with proficiency level."""
    level: str  # "Beginner" | "Intermediate" | "Advanced"


class UserBase(BaseModel):
    name: str
    email: EmailStr
    bio: Optional[str] = ""
    avatar: Optional[str] = ""          # initials or URL
    skills_offered: Dict[str, str] = {} # {"Python": "Intermediate"}
    skills_needed: Dict[str, str] = {}  # {"React": "Beginner"}


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: str
    coins: int = 100               # Starting balance
    trust_score: float = 50.0      # 0–100
    total_sessions: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class UserInDB(UserOut):
    hashed_password: str


# ─── DB helpers ──────────────────────────────────────────────────────────────
def user_from_doc(doc: dict) -> dict:
    """Convert MongoDB _id to string id."""
    doc["id"] = str(doc.pop("_id"))
    return doc