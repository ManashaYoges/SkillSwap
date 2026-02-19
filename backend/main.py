"""
main.py
FastAPI application entry point for SkillSwap AI backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.database import connect_db, close_db
from routes.auth_routes import router as auth_router
from routes.match_routes import router as match_router
from routes.recommendation_routes import router as rec_router
from routes.session_routes import router as session_router

app = FastAPI(
    title="SkillSwap AI API",
    version="1.0.0",
    description="Peer-to-peer skill exchange platform with AI-powered matching.",
)

# ─── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── DB Lifecycle ─────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    await connect_db()


@app.on_event("shutdown")
async def shutdown():
    await close_db()


# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(match_router)
app.include_router(rec_router)
app.include_router(session_router)


# ─── Extra: Coin Ledger + Leaderboard ─────────────────────────────────────────
from fastapi import Depends
from routes.auth_routes import get_current_user
from services.coin_service import get_ledger
from config.database import users_col


@app.get("/coins/ledger", tags=["Coins"])
async def coin_ledger(current_user: dict = Depends(get_current_user)):
    """Return the current user's SkillCoin transaction history."""
    txs = await get_ledger(current_user["id"])
    return {"ledger": txs, "balance": current_user["coins"]}


@app.get("/leaderboard", tags=["Leaderboard"])
async def leaderboard(by: str = "coins"):
    """
    Global leaderboard.
    by=coins  → sort by coin balance
    by=trust  → sort by trust_score
    """
    sort_field = "coins" if by == "coins" else "trust_score"
    cursor = (
        users_col()
        .find({}, {"hashed_password": 0})
        .sort(sort_field, -1)
        .limit(10)
    )
    board = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        board.append({
            "id": doc["id"],
            "name": doc["name"],
            "avatar": doc.get("avatar", "?"),
            "coins": doc.get("coins", 0),
            "trust_score": doc.get("trust_score", 50.0),
            "total_sessions": doc.get("total_sessions", 0),
        })
    return {"leaderboard": board, "sorted_by": sort_field}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}