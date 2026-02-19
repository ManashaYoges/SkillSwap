from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId
from app.models.user import UserRegister, UserLogin, TokenResponse, UserProfile
from app.core.security import hash_password, verify_password, create_access_token
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

def _format_user(u: dict) -> UserProfile:
    return UserProfile(
        id=str(u["_id"]),
        name=u["name"],
        email=u["email"],
        skills_offered=u.get("skills_offered", []),
        skills_wanted=u.get("skills_wanted", []),
        skill_coins=u.get("skill_coins", 0),
        trust_score=u.get("trust_score", 100.0),
        level=u.get("level", 1),
        sessions_completed=u.get("sessions_completed", 0),
        rating=u.get("rating", 5.0),
        badges=u.get("badges", []),
        location=u.get("location"),
        created_at=u.get("created_at", datetime.utcnow()),
    )

@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister):
    db = get_db()
    # Check duplicate email
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "name":               data.name,
        "email":              data.email,
        "password_hash":      hash_password(data.password),
        "skills_offered":     [s.model_dump() for s in data.skills_offered],
        "skills_wanted":      data.skills_wanted,
        "skill_coins":        100,   # welcome bonus
        "trust_score":        100.0,
        "level":              1,
        "sessions_completed": 0,
        "rating":             5.0,
        "badges":             ["Early Adopter"],
        "location":           data.location,
        "fraud_flagged":      False,
        "created_at":         datetime.utcnow(),
    }
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    # Log welcome bonus in ledger
    await db.ledger.insert_one({
        "user_id":     str(result.inserted_id),
        "type":        "earned",
        "amount":      100,
        "description": "🎁 Welcome Bonus — Account created",
        "created_at":  datetime.utcnow(),
    })

    token = create_access_token({"sub": str(result.inserted_id)})
    return TokenResponse(access_token=token, user=_format_user(user_doc))


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    db = get_db()
    user = await db.users.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user["_id"])})
    return TokenResponse(access_token=token, user=_format_user(user))
