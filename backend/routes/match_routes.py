"""
routes/match_routes.py
AI-powered skill matching & recommendations.
"""
from fastapi import APIRouter, Depends, HTTPException

from config.database import users_col
from routes.auth_routes import get_current_user
from ai.recommendation_engine import recommend_users
from ai.skill_matching import explain_match
from models.user_model import user_from_doc

router = APIRouter(prefix="/match", tags=["Matching"])


@router.get("/recommendations")
async def get_recommendations(
    top_n: int = 5,
    current_user: dict = Depends(get_current_user),
):
    """
    Return top N AI-matched users for the current user based on their
    skills_needed vs other users' skills_offered.
    """
    if not current_user.get("skills_needed"):
        raise HTTPException(
            status_code=400,
            detail="Add skills you want to learn first (skills_needed).",
        )

    # Fetch all users except self
    cursor = users_col().find(
        {"_id": {"$ne": current_user["id"]}},
        {"hashed_password": 0},
    )
    all_users = []
    async for doc in cursor:
        u = user_from_doc(doc)
        if u.get("skills_offered"):
            all_users.append(u)

    recommendations = recommend_users(current_user, all_users, top_n=top_n)

    # Enrich with trust scores from DB
    for rec in recommendations:
        db_user = await users_col().find_one({"_id": __import__("bson").ObjectId(rec["id"])})
        if db_user:
            rec["trust_score"] = db_user.get("trust_score", 50.0)
            rec["total_sessions"] = db_user.get("total_sessions", 0)
            rec["avatar"] = db_user.get("avatar", "?")
            rec["bio"] = db_user.get("bio", "")

    return {"recommendations": recommendations, "count": len(recommendations)}


@router.get("/explain/{target_user_id}")
async def explain_match_detail(
    target_user_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Explain why two users are a good match.
    """
    import bson
    target = await users_col().find_one({"_id": bson.ObjectId(target_user_id)})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target = user_from_doc(target)
    explanation = explain_match(current_user["skills_needed"], target["skills_offered"])

    return {
        "you": {"id": current_user["id"], "skills_needed": current_user["skills_needed"]},
        "them": {"id": target["id"], "name": target["name"], "skills_offered": target["skills_offered"]},
        "match": explanation,
    }