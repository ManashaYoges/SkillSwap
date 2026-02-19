from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from datetime import datetime
from app.core.security import decode_token
from app.core.database import get_db
from app.models.user import UserProfile, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])
security = HTTPBearer()

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(creds.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def _fmt(u):
    return {
        "id":                 str(u["_id"]),
        "name":               u["name"],
        "email":              u["email"],
        "skills_offered":     u.get("skills_offered", []),
        "skills_wanted":      u.get("skills_wanted", []),
        "skill_coins":        u.get("skill_coins", 0),
        "trust_score":        u.get("trust_score", 100.0),
        "level":              u.get("level", 1),
        "sessions_completed": u.get("sessions_completed", 0),
        "rating":             u.get("rating", 5.0),
        "badges":             u.get("badges", []),
        "location":           u.get("location"),
        "created_at":         u.get("created_at", datetime.utcnow()).isoformat(),
    }

@router.get("/me")
async def get_profile(current_user=Depends(get_current_user)):
    return _fmt(current_user)

@router.put("/me")
async def update_profile(data: UserUpdate, current_user=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if "skills_offered" in update_data:
        update_data["skills_offered"] = [s.model_dump() if hasattr(s, 'model_dump') else s for s in update_data["skills_offered"]]
    await db.users.update_one({"_id": current_user["_id"]}, {"$set": update_data})
    updated = await db.users.find_one({"_id": current_user["_id"]})
    return _fmt(updated)

@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    db = get_db()
    # Top by SkillCoins
    coins_cursor = db.users.find({}, {"password_hash": 0}).sort("skill_coins", -1).limit(limit)
    by_coins = []
    async for u in coins_cursor:
        by_coins.append({
            "id": str(u["_id"]), "name": u["name"],
            "skill_coins": u.get("skill_coins", 0),
            "trust_score": u.get("trust_score", 100),
            "sessions_completed": u.get("sessions_completed", 0),
            "badges": u.get("badges", []),
        })

    # Top by Trust Score
    trust_cursor = db.users.find({}, {"password_hash": 0}).sort("trust_score", -1).limit(limit)
    by_trust = []
    async for u in trust_cursor:
        by_trust.append({
            "id": str(u["_id"]), "name": u["name"],
            "skill_coins": u.get("skill_coins", 0),
            "trust_score": u.get("trust_score", 100),
            "sessions_completed": u.get("sessions_completed", 0),
            "badges": u.get("badges", []),
        })

    return {"by_coins": by_coins, "by_trust": by_trust}
