# app/main.py
from fastapi import FastAPI
from .routes import org_routes, auth_routes

app = FastAPI(title="Organization Management Service")

app.include_router(auth_routes.router)
app.include_router(org_routes.router)

@app.get("/")
def home():
    return {"message": "Organization Management Service is running"}
