"""
services/coin_service.py
SkillCoin balance helpers used across routes.
"""
import bson
from config.database import users_col, transactions_col
from datetime import datetime


async def get_balance(user_id: str) -> int:
    user = await users_col().find_one({"_id": bson.ObjectId(user_id)})
    return user.get("coins", 0) if user else 0


async def award_coins(user_id: str, amount: int, description: str, session_id: str = None):
    """Add coins to a user and log the transaction."""
    await users_col().update_one(
        {"_id": bson.ObjectId(user_id)},
        {"$inc": {"coins": amount}},
    )
    await transactions_col().insert_one({
        "user_id": user_id,
        "type": "earned",
        "amount": amount,
        "description": description,
        "session_id": session_id,
        "created_at": datetime.utcnow(),
    })


async def deduct_coins(user_id: str, amount: int, description: str, session_id: str = None):
    """Subtract coins from a user and log the transaction."""
    user = await users_col().find_one({"_id": bson.ObjectId(user_id)})
    if not user or user.get("coins", 0) < amount:
        raise ValueError("Insufficient SkillCoins")
    await users_col().update_one(
        {"_id": bson.ObjectId(user_id)},
        {"$inc": {"coins": -amount}},
    )
    await transactions_col().insert_one({
        "user_id": user_id,
        "type": "spent",
        "amount": -amount,
        "description": description,
        "session_id": session_id,
        "created_at": datetime.utcnow(),
    })


async def get_ledger(user_id: str, limit: int = 20) -> list:
    """Return recent transactions for a user."""
    cursor = (
        transactions_col()
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(limit)
    )
    txs = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        txs.append(doc)
    return txs