"""
routes/session_routes.py
Session request, confirmation & listing.
"""
from datetime import datetime

import bson
from fastapi import APIRouter, Depends, HTTPException

from config.database import sessions_col, users_col, transactions_col
from models.session_model import SessionCreate, SessionConfirm, session_from_doc
from routes.auth_routes import get_current_user

router = APIRouter(prefix="/sessions", tags=["Sessions"])

SESSION_COST = 10       # SkillCoins deducted from requester
SESSION_REWARD = 10     # SkillCoins awarded to provider
TRUST_DELTA = 2.0       # Trust increase on completed session


async def _update_coins(user_id: str, delta: int, description: str, tx_type: str, session_id: str):
    """Update user coins and log transaction."""
    await users_col().update_one(
        {"_id": bson.ObjectId(user_id)},
        {"$inc": {"coins": delta}},
    )
    await transactions_col().insert_one({
        "user_id": user_id,
        "type": tx_type,
        "amount": delta,
        "description": description,
        "session_id": session_id,
        "created_at": datetime.utcnow(),
    })


@router.post("/request", status_code=201)
async def request_session(
    data: SessionCreate,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a session request. Deducts SESSION_COST coins from requester.
    """
    # Validate provider exists
    provider = await users_col().find_one({"_id": bson.ObjectId(data.provider_id)})
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Check requester has enough coins
    if current_user["coins"] < SESSION_COST:
        raise HTTPException(status_code=402, detail="Insufficient SkillCoins")

    session_doc = {
        "requester_id": current_user["id"],
        "provider_id": data.provider_id,
        "requester_name": current_user["name"],
        "provider_name": provider["name"],
        "skill": data.skill,
        "status": "pending",
        "coins_spent": SESSION_COST,
        "coins_earned": SESSION_REWARD,
        "scheduled_at": data.scheduled_at,
        "completed_at": None,
        "notes": data.notes,
        "created_at": datetime.utcnow(),
    }
    result = await sessions_col().insert_one(session_doc)
    session_id = str(result.inserted_id)

    # Deduct coins from requester immediately on request
    await _update_coins(
        current_user["id"],
        -SESSION_COST,
        f"Session requested: {data.skill} with {provider['name']}",
        "spent",
        session_id,
    )

    return {"message": "Session requested", "session_id": session_id}


@router.post("/confirm")
async def confirm_session(
    data: SessionConfirm,
    current_user: dict = Depends(get_current_user),
):
    """
    Provider confirms (completes) the session.
    Awards coins to provider and increases trust scores.
    """
    session = await sessions_col().find_one({"_id": bson.ObjectId(data.session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["provider_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the provider can confirm")
    if session["status"] != "pending":
        raise HTTPException(status_code=400, detail="Session already processed")

    # Mark session complete
    await sessions_col().update_one(
        {"_id": bson.ObjectId(data.session_id)},
        {"$set": {"status": "completed", "completed_at": datetime.utcnow()}},
    )

    # Award coins to provider
    await _update_coins(
        current_user["id"],
        SESSION_REWARD,
        f"Session completed: {session['skill']} with {session['requester_name']}",
        "earned",
        data.session_id,
    )

    # Increment session count and trust score for both users
    for uid in [session["requester_id"], session["provider_id"]]:
        user = await users_col().find_one({"_id": bson.ObjectId(uid)})
        new_trust = min(100.0, user.get("trust_score", 50.0) + TRUST_DELTA)
        await users_col().update_one(
            {"_id": bson.ObjectId(uid)},
            {"$inc": {"total_sessions": 1}, "$set": {"trust_score": new_trust}},
        )

    return {"message": "Session confirmed and coins awarded"}


@router.get("/my")
async def my_sessions(current_user: dict = Depends(get_current_user)):
    """
    Return all sessions for the current user (as requester or provider).
    """
    cursor = sessions_col().find(
        {"$or": [
            {"requester_id": current_user["id"]},
            {"provider_id": current_user["id"]},
        ]}
    ).sort("created_at", -1)

    sessions = []
    async for doc in cursor:
        sessions.append(session_from_doc(doc))
    return {"sessions": sessions}


@router.get("/{session_id}")
async def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    session = await sessions_col().find_one({"_id": bson.ObjectId(session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Not found")
    return session_from_doc(session)