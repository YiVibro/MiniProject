from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
import os

router = APIRouter()

# Setup OAuth
oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)

    # Save user in session
    request.session["user"] = dict(user)

    # If you want to store user in Supabase DB:
    # from app.database.db import supabase
    # supabase.table("users").upsert({
    #     "name": user.get("name"),
    #     "email": user.get("email"),
    #     "profile_pic": user.get("picture"),
    # }).execute()

    return RedirectResponse(url="/oauth/protected")

@router.get("/protected")
async def protected(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/oauth/login")
    return {"message": f"Hello {user['email']}"}

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}
