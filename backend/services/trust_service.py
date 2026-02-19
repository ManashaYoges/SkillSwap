"""
services/trust_service.py
Trust score management.
"""
import bson
from config.database import users_col


TRUST_MIN = 0.0
TRUST_MAX = 100.0


def trust_label(score: float) -> str:
    if score >= 85:
        return "Highly Trusted"
    if score >= 65:
        return "Trusted"
    if score >= 45:
        return "Building Trust"
    return "New Member"


async def increase_trust(user_id: str, delta: float = 2.0):
    user = await users_col().find_one({"_id": bson.ObjectId(user_id)})
    if not user:
        return
    new_score = min(TRUST_MAX, user.get("trust_score", 50.0) + delta)
    await users_col().update_one(
        {"_id": bson.ObjectId(user_id)},
        {"$set": {"trust_score": round(new_score, 1)}},
    )
    return new_score


async def decrease_trust(user_id: str, delta: float = 5.0):
    user = await users_col().find_one({"_id": bson.ObjectId(user_id)})
    if not user:
        return
    new_score = max(TRUST_MIN, user.get("trust_score", 50.0) - delta)
    await users_col().update_one(
        {"_id": bson.ObjectId(user_id)},
        {"$set": {"trust_score": round(new_score, 1)}},
    )
    return new_score


async def get_trust(user_id: str) -> dict:
    user = await users_col().find_one({"_id": bson.ObjectId(user_id)})
    if not user:
        return {}
    score = user.get("trust_score", 50.0)
    return {"score": score, "label": trust_label(score)}