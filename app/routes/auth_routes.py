# app/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, status
from ..db import master_db
from ..models.admin import AdminLogin, Token
from ..core.security import verify_password, create_access_token
from bson import ObjectId
from datetime import timedelta
from ..config import settings

router = APIRouter(prefix="/admin", tags=["auth"])

@router.post("/login", response_model=Token)
async def admin_login(payload: AdminLogin):
    admins = master_db["admins"]
    orgs = master_db["organizations"]

    admin = await admins.find_one({"email": payload.email})
    if not admin or not verify_password(payload.password, admin["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials")

    org = await orgs.find_one({"admin_id": admin["_id"]})
    if not org:
        raise HTTPException(status_code=400, detail="Admin not linked to organization")

    token_data = {
        "admin_id": str(admin["_id"]),
        "org_id": str(org["_id"]),
        "org_name": org["organization_name"]
    }

    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(access_token=access_token)
