# app/routes/org_routes.py
from fastapi import APIRouter, HTTPException, status
from ..db import master_db, get_org_collection
from ..models.organization import OrganizationCreate, OrganizationResponse
from ..core.security import hash_password
from bson import ObjectId

router = APIRouter(prefix="/org", tags=["organizations"])

@router.post("/create", response_model=OrganizationResponse)
async def create_org(payload: OrganizationCreate):
    orgs = master_db["organizations"]
    admins = master_db["admins"]

    existing = await orgs.find_one({"organization_name": payload.organization_name})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Organization name already exists")

    # Create admin
    admin_doc = {
        "email": payload.email,
        "password_hash": hash_password(payload.password),
    }
    admin_result = await admins.insert_one(admin_doc)

    collection_name = f"org_{payload.organization_name}"
    await master_db.create_collection(collection_name)  # optional; Mongo will auto-create on first insert

    org_doc = {
        "organization_name": payload.organization_name,
        "collection_name": collection_name,
        "admin_id": admin_result.inserted_id,
    }
    org_result = await orgs.insert_one(org_doc)

    return OrganizationResponse(
        id=str(org_result.inserted_id),
        organization_name=payload.organization_name,
        collection_name=collection_name,
        admin_email=payload.email,
    )

from ..models.organization import OrganizationGet

@router.get("/get")
async def get_org(organization_name: str):
    orgs = master_db["organizations"]
    org = await orgs.find_one({"organization_name": organization_name})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    org["id"] = str(org["_id"])
    org["admin_id"] = str(org["admin_id"])
    del org["_id"]
    return org


from fastapi import Depends
from ..core.deps import get_current_admin
from ..models.organization import OrganizationUpdate

@router.put("/update")
async def update_org(payload: OrganizationUpdate, current = Depends(get_current_admin)):
    orgs = master_db["organizations"]
    admins = master_db["admins"]

    # verify admin email/password matches current admin (you can re-check password or rely on token)
    admin = current["admin"]
    if admin["email"] != payload.email:
        raise HTTPException(status_code=403, detail="Not allowed")

    # check old org exists and belongs to this admin
    old_org = await orgs.find_one({"organization_name": payload.old_organization_name,
                                   "admin_id": admin["_id"]})
    if not old_org:
        raise HTTPException(status_code=404, detail="Organization not found or not owned by admin")

    # ensure new name not taken
    existing = await orgs.find_one({"organization_name": payload.new_organization_name})
    if existing:
        raise HTTPException(status_code=400, detail="New organization name already exists")

    old_coll = master_db[old_org["collection_name"]]
    new_collection_name = f"org_{payload.new_organization_name}"
    new_coll = master_db[new_collection_name]

    # migrate data (simple version)
    cursor = old_coll.find({})
    async for doc in cursor:
        doc["_id"] = ObjectId()  # avoid duplicate _id
        await new_coll.insert_one(doc)

    await old_coll.drop()

    await orgs.update_one(
        {"_id": old_org["_id"]},
        {"$set": {
            "organization_name": payload.new_organization_name,
            "collection_name": new_collection_name
        }}
    )

    return {"message": "Organization updated successfully"}


from ..core.deps import get_current_admin

@router.delete("/delete")
async def delete_org(organization_name: str, current = Depends(get_current_admin)):
    admin = current["admin"]
    orgs = master_db["organizations"]
    admins = master_db["admins"]

    org = await orgs.find_one({"organization_name": organization_name, "admin_id": admin["_id"]})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found or not owned by admin")

    # Drop collection
    coll_name = org["collection_name"]
    await master_db[coll_name].drop()

    await orgs.delete_one({"_id": org["_id"]})
    await admins.delete_one({"_id": admin["_id"]})  # optional

    return {"message": "Organization deleted successfully"}
