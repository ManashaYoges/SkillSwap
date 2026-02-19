from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import connect_db, close_db
from app.routes import auth, users, matching, sessions, ledger

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(
    title="SkillSwap AI API",
    description="AI-powered peer-to-peer skill exchange platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(matching.router)
app.include_router(sessions.router)
app.include_router(ledger.router)

@app.get("/")
async def root():
    return {
        "message": "⚡ SkillSwap AI Backend",
        "docs":    "/docs",
        "status":  "running",
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
