"""
services/matching_service.py
High-level service that glues DB queries with AI matching logic.
"""
from config.database import users_col
from models.user_model import user_from_doc
from ai.recommendation_engine import recommend_users


async def get_matches_for_user(user: dict, top_n: int = 5) -> list:
    """
    Fetch all eligible users from DB and run AI recommendation.
    """
    cursor = users_col().find(
        {"_id": {"$ne": __import__("bson").ObjectId(user["id"])}},
        {"hashed_password": 0},
    )
    candidates = []
    async for doc in cursor:
        u = user_from_doc(doc)
        if u.get("skills_offered"):
            candidates.append(u)

    return recommend_users(user, candidates, top_n=top_n)