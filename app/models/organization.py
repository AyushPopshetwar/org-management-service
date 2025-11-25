# app/models/organization.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from bson import ObjectId

class OrganizationCreate(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrganizationResponse(BaseModel):
    id: str
    organization_name: str
    collection_name: str
    admin_email: EmailStr

class OrganizationGet(BaseModel):
    organization_name: str

class OrganizationUpdate(BaseModel):
    # For clarity: old name & new name
    old_organization_name: str
    new_organization_name: str
    email: EmailStr
    password: str
