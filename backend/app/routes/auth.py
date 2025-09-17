from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt
from app.database.db import supabase

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

@router.post("/signup")
async def signup(req: SignupRequest):
    hashed_pw = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt()).decode()

    response = supabase.table("users").insert({
        "name": req.name,
        "email": req.email,
        "password_hash": hashed_pw,
        "profile_pic": ""
    }).execute()

    if response.data:
        return {"message": "User created", "user": response.data[0]}
    raise HTTPException(status_code=400, detail="Failed to create user")


@router.post("/login")
async def login(req: LoginRequest):
    response = supabase.table("users").select("*").eq("email", req.email).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = response.data[0]

    if bcrypt.checkpw(req.password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return {"message": "Login successful", "user": user}
    else:
        raise HTTPException(status_code=401, detail="Invalid password")
