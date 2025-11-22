from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from app.routes.course_routes import router as course_router
from app.routes import course_routes
from app.routes.agents import router as agents_router
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
# Support multiple origins via comma-separated env var; default to common dev ports
FRONTEND_ORIGINS = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://localhost:8080,http://127.0.0.1:5173,http://127.0.0.1:8080",
)
ALLOWED_ORIGINS = [o.strip() for o in FRONTEND_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.routes import auth, oauth, agents

# Include all routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(oauth.router, prefix="/oauth", tags=["OAuth"])
app.include_router(agents.router, tags=["Agents"])
app.include_router(course_routes.router, prefix="/course", tags=["Course"])
app.include_router(course_router)
app.include_router(agents_router)

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI with Supabase + Google OAuth"}
