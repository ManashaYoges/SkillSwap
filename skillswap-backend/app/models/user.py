from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# ── Skill sub-model ──────────────────────────────────────────────────────────
class Skill(BaseModel):
    name: str
    level: str = "Beginner"   # Beginner / Intermediate / Advanced
    mastery: float = 0.0      # 0-100

# ── Registration ─────────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    skills_offered: List[Skill] = []
    skills_wanted: List[str] = []
    location: Optional[str] = None

# ── Login ─────────────────────────────────────────────────────────────────────
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ── Public profile (returned to client) ──────────────────────────────────────
class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    skills_offered: List[Skill]
    skills_wanted: List[str]
    skill_coins: int = 0
    trust_score: float = 100.0
    level: int = 1
    sessions_completed: int = 0
    rating: float = 5.0
    badges: List[str] = []
    location: Optional[str] = None
    created_at: datetime

# ── Token response ────────────────────────────────────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile

# ── Update profile ────────────────────────────────────────────────────────────
class UserUpdate(BaseModel):
    name: Optional[str] = None
    skills_offered: Optional[List[Skill]] = None
    skills_wanted: Optional[List[str]] = None
    location: Optional[str] = None
