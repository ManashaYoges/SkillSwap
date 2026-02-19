"""
config/database.py
MongoDB connection via PyMongo / Motor (async).
Set MONGO_URI in your .env file.
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "skillswap")

client: AsyncIOMotorClient = None


async def connect_db():
    global client
    client = AsyncIOMotorClient(MONGO_URI)
    print(f"[DB] Connected to MongoDB at {MONGO_URI}")


async def close_db():
    global client
    if client:
        client.close()
        print("[DB] MongoDB connection closed")


def get_db():
    return client[DB_NAME]


# ─── Collection helpers ──────────────────────────────────────────────────────
def users_col():
    return get_db()["users"]

def sessions_col():
    return get_db()["sessions"]

def transactions_col():
    return get_db()["transactions"]

def skills_col():
    return get_db()["skills"]