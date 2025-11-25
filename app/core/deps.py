from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from bson import ObjectId
from ..config import settings
from ..db import master_db

security = HTTPBearer()

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        admin_id: str = payload.get("admin_id")
        org_id: str = payload.get("org_id")

        if admin_id is None or org_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    admin = await master_db["admins"].find_one({"_id": ObjectId(admin_id)})
    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found")

    return {"admin": admin, "org_id": org_id}
