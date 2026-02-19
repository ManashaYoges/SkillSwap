from fastapi import APIRouter, Depends
from app.routes.users import get_current_user
from app.core.database import get_db

router = APIRouter(prefix="/ledger", tags=["Ledger"])

@router.get("/")
async def get_ledger(current_user=Depends(get_current_user)):
    db = get_db()
    uid = str(current_user["_id"])
    transactions = []
    async for t in db.ledger.find({"user_id": uid}).sort("created_at", -1).limit(50):
        transactions.append({
            "id":          str(t["_id"]),
            "type":        t["type"],
            "amount":      t["amount"],
            "description": t["description"],
            "session_id":  t.get("session_id"),
            "created_at":  t["created_at"].isoformat(),
        })

    total_earned = sum(t["amount"] for t in transactions if t["type"] == "earned")
    total_spent  = sum(t["amount"] for t in transactions if t["type"] == "spent")
    balance      = current_user.get("skill_coins", 0)

    return {
        "balance":      balance,
        "total_earned": total_earned,
        "total_spent":  total_spent,
        "transactions": transactions,
    }
