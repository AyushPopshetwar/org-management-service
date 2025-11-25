# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
master_db = client[settings.MASTER_DB_NAME]

def get_org_collection(org_name: str):
    collection_name = f"org_{org_name}"
    return master_db[collection_name]  # or use a separate DB if you want
