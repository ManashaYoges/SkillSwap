"""
routes/auth_routes.py
Registration, Login, and /me endpoint.
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from config.database import users_col, transactions_col
from models.user_model import UserCreate, UserOut, user_from_doc

router = APIRouter(prefix="/auth", tags=["Auth"])

# ─── Config ──────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production-please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

STARTING_COINS = 100


# ─── Helpers ─────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await users_col().find_one({"_id": ObjectId(user_id)})
    if not user:
        raise credentials_exception
    return user_from_doc(user)


# ─── Routes ──────────────────────────────────────────────────────────────────
@router.post("/register", response_model=dict, status_code=201)
async def register(data: UserCreate):
    col = users_col()

    # Check duplicate email
    existing = await col.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    doc = {
        "name": data.name,
        "email": data.email,
        "bio": data.bio,
        "avatar": data.avatar or data.name[:2].upper(),
        "hashed_password": hash_password(data.password),
        "skills_offered": data.skills_offered,
        "skills_needed": data.skills_needed,
        "coins": STARTING_COINS,
        "trust_score": 50.0,
        "total_sessions": 0,
        "created_at": datetime.utcnow(),
    }
    result = await col.insert_one(doc)
    user_id = str(result.inserted_id)

    # Welcome bonus transaction
    await transactions_col().insert_one({
        "user_id": user_id,
        "type": "earned",
        "amount": STARTING_COINS,
        "description": "Welcome bonus",
        "session_id": None,
        "created_at": datetime.utcnow(),
    })

    token = create_access_token({"sub": user_id})
    return {"access_token": token, "token_type": "bearer", "user_id": user_id}


@router.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    col = users_col()
    user = await col.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user["_id"])})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def me(current_user: dict = Depends(get_current_user)):
    return current_user