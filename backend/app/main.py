# from fastapi import FastAPI,HTTPException
# import bcrypt
# from app.database.db import supabase

# app=FastAPI()

# @app.post("/signup")
# def signup(name:str,email:str,password:str):
#     #hash password
#     hashed_pw=bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt()).decode()

#     # Insert into Supabase
#     response = supabase.table("users").insert({
#         "name": name,
#         "email": email,
#         "password_hash": hashed_pw,
#         "profile_pic": ""
#     }).execute()

#     if response.data:
#         return {"message": "User created", "user": response.data}
    

# @app.post("/login")
# def login(email:str,password:str):
#     #fetch user details
#     response=supabase.table("users").select("*").eq("email",email).execute()

#     if not response.data:
#         raise HTTPException(status_code=404, detail="User not found")
   
#     user=response.data[0]

#     #verify password
#     if bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
#         return {"message": "Login successful", "user": user}
#     else:
#         raise HTTPException(status_code=401, detail="Invalid password")

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load env
load_dotenv()

app = FastAPI()

# Add session middleware (needed for OAuth user sessions)
# Configure cookie for cross-site usage (frontend and backend on different origins)
SESSION_SAMESITE = os.getenv("SESSION_SAMESITE", "none").lower()
SESSION_HTTPS_ONLY = os.getenv("SESSION_HTTPS_ONLY", "false").lower() == "true"
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "supersecret_session_key"),
    same_site=SESSION_SAMESITE,   # "none" for cross-site XHR
    https_only=SESSION_HTTPS_ONLY # set true in production over HTTPS
)

# CORS for frontend
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.routes import auth, oauth

# Include both routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(oauth.router, prefix="/oauth", tags=["OAuth"])

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI with Supabase + Google OAuth"}
