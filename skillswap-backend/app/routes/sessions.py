from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime
from app.routes.users import get_current_user
from app.core.database import get_db
from app.models.session import SessionCreate
from app.services.trust import recalculate_trust, award_badges, detect_fraud

router = APIRouter(prefix="/sessions", tags=["Sessions"])

COINS_PER_SESSION = 30   # coins earned for teaching

def _fmt_session(s):
    return {
        "id":               str(s["_id"]),
        "requester_id":     s["requester_id"],
        "partner_id":       s["partner_id"],
        "partner_name":     s.get("partner_name", ""),
        "skill":            s["skill"],
        "scheduled_time":   s["scheduled_time"].isoformat(),
        "duration_minutes": s.get("duration_minutes", 60),
        "status":           s["status"],
        "coins_earned":     s.get("coins_earned"),
        "created_at":       s["created_at"].isoformat(),
    }

@router.post("/")
async def create_session(data: SessionCreate, current_user=Depends(get_current_user)):
    db = get_db()

    # Validate partner exists
    partner = await db.users.find_one({"_id": ObjectId(data.partner_id)})
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    # Fraud check before allowing new session
    recent = []
    async for s in db.sessions.find({"requester_id": str(current_user["_id"])}):
        recent.append(s)
    fraud = detect_fraud(current_user, recent)
    if fraud["flagged"]:
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": {"fraud_flagged": True}}
        )
        raise HTTPException(status_code=403, detail=f"Session blocked: {fraud['reason']}")

    session_doc = {
        "requester_id":     str(current_user["_id"]),
        "partner_id":       data.partner_id,
        "partner_name":     partner["name"],
        "skill":            data.skill,
        "scheduled_time":   data.scheduled_time,
        "duration_minutes": data.duration_minutes,
        "status":           "pending",
        "coins_earned":     None,
        "created_at":       datetime.utcnow(),
    }
    result = await db.sessions.insert_one(session_doc)
    session_doc["_id"] = result.inserted_id
    return _fmt_session(session_doc)

@router.get("/")
async def get_sessions(current_user=Depends(get_current_user)):
    db = get_db()
    uid = str(current_user["_id"])
    sessions = []
    async for s in db.sessions.find({
        "$or": [{"requester_id": uid}, {"partner_id": uid}]
    }).sort("scheduled_time", -1):
        sessions.append(_fmt_session(s))
    return sessions

@router.put("/{session_id}/confirm")
async def confirm_session(session_id: str, current_user=Depends(get_current_user)):
    db = get_db()
    session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["partner_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Only the partner can confirm")
    if session["status"] != "pending":
        raise HTTPException(status_code=400, detail="Session already confirmed or completed")

    await db.sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"status": "confirmed"}}
    )
    return {"message": "Session confirmed"}

@router.put("/{session_id}/complete")
async def complete_session(session_id: str, current_user=Depends(get_current_user)):
    db = get_db()
    session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["status"] != "confirmed":
        raise HTTPException(status_code=400, detail="Session must be confirmed first")

    uid = str(current_user["_id"])
    if uid not in [session["requester_id"], session["partner_id"]]:
        raise HTTPException(status_code=403, detail="Not part of this session")

    # Mark complete + award coins to teacher (requester)
    await db.sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"status": "completed", "coins_earned": COINS_PER_SESSION}}
    )

    requester_id = session["requester_id"]

    # Add coins to teacher
    await db.users.update_one(
        {"_id": ObjectId(requester_id)},
        {"$inc": {"skill_coins": COINS_PER_SESSION, "sessions_completed": 1}}
    )

    # Ledger: earned
    await db.ledger.insert_one({
        "user_id":     requester_id,
        "type":        "earned",
        "amount":      COINS_PER_SESSION,
        "description": f"📚 Taught {session['skill']}",
        "session_id":  session_id,
        "created_at":  datetime.utcnow(),
    })

    # Deduct coins from learner (partner)
    partner_id = session["partner_id"]
    cost = max(COINS_PER_SESSION - 10, 10)
    await db.users.update_one(
        {"_id": ObjectId(partner_id)},
        {"$inc": {"skill_coins": -cost, "sessions_completed": 1}}
    )
    await db.ledger.insert_one({
        "user_id":     partner_id,
        "type":        "spent",
        "amount":      cost,
        "description": f"🎓 Learned {session['skill']}",
        "session_id":  session_id,
        "created_at":  datetime.utcnow(),
    })

    # Recalculate trust + badges for both users
    for uid_str in [requester_id, partner_id]:
        user_doc = await db.users.find_one({"_id": ObjectId(uid_str)})
        recent_sessions = []
        async for s in db.sessions.find({"$or": [{"requester_id": uid_str}, {"partner_id": uid_str}]}):
            recent_sessions.append(s)
        new_trust  = recalculate_trust(user_doc, recent_sessions)
        new_badges = award_badges({**user_doc, "trust_score": new_trust})
        level      = max(1, user_doc.get("sessions_completed", 0) // 3 + 1)
        await db.users.update_one(
            {"_id": ObjectId(uid_str)},
            {"$set": {"trust_score": new_trust, "badges": new_badges, "level": level}}
        )

    return {"message": "Session completed", "coins_awarded": COINS_PER_SESSION}
