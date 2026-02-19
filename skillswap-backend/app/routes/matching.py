from fastapi import APIRouter, Depends
from app.routes.users import get_current_user
from app.core.database import get_db
from app.services.matching import get_matches

router = APIRouter(prefix="/matching", tags=["Matching"])

@router.get("/")
async def find_matches(top_n: int = 5, current_user=Depends(get_current_user)):
    db = get_db()
    # Fetch all other users (exclude passwords)
    all_users = []
    async for u in db.users.find({}, {"password_hash": 0}):
        all_users.append(u)

    matches = get_matches(current_user, all_users, top_n=top_n)
    return {
        "total_scanned": len(all_users) - 1,
        "matches_found": len(matches),
        "matches": matches,
    }
