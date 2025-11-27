from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.database.db import supabase

router = APIRouter(prefix="/api/profile", tags=["profile"])


# Pydantic models
class UserProfile(BaseModel):
    user_id: str
    name: Optional[str] = None
    bio: Optional[str] = None
    study_goal: Optional[str] = None
    preferred_subjects: List[str] = []
    weekly_goal: int = 30
    avatar_url: Optional[str] = None

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    study_goal: Optional[str] = None
    preferred_subjects: Optional[List[str]] = None
    weekly_goal: Optional[int] = None

class UserStats(BaseModel):
    user_id: str
    total_study_hours: int
    courses_completed: int
    current_streak: int
    longest_streak: int
    ai_interactions: int
    study_hours_this_week: int
    last_activity_date: Optional[str] = None
    total_xp: Optional[int] = 0
    current_level: Optional[int] = 1
    xp_to_next_level: Optional[int] = 100
    total_points: Optional[int] = 0

class Achievement(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    earned: bool
    progress: int = 0
    earned_at: Optional[str] = None

class AwardXPRequest(BaseModel):
    user_id: str
    amount: int
    reason: Optional[str] = ""

class UnlockAchievementRequest(BaseModel):
    user_id: str
    achievement_id: str

class CompleteChallengeRequest(BaseModel):
    user_id: str
    challenge_id: str

# Helper function to get user from authorization header
async def get_current_user(authorization: str = None) -> str:
    """Extract user ID from Supabase JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    try:
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@router.get("/", response_model=UserProfile)
async def get_profile(user_id: str):
    """Get user profile by user_id"""
    try:
        response = supabase.table("user_profiles").select("*").eq("user_id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            # Create default profile if it doesn't exist
            default_profile = {
                "user_id": user_id,
                "name": "",
                "bio": "",
                "study_goal": "",
                "preferred_subjects": [],
                "weekly_goal": 30,
                "avatar_url": None
            }
            create_response = supabase.table("user_profiles").insert(default_profile).execute()
            return UserProfile(**create_response.data[0])
        
        profile_data = response.data[0]
        return UserProfile(**profile_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {str(e)}")

@router.put("/", response_model=UserProfile)
async def update_profile(user_id: str, profile_update: UserProfileUpdate):
    """Update user profile"""
    try:
        # Build update dict with only provided fields
        update_data = {}
        if profile_update.name is not None:
            update_data["name"] = profile_update.name
        if profile_update.bio is not None:
            update_data["bio"] = profile_update.bio
        if profile_update.study_goal is not None:
            update_data["study_goal"] = profile_update.study_goal
        if profile_update.preferred_subjects is not None:
            update_data["preferred_subjects"] = profile_update.preferred_subjects
        if profile_update.weekly_goal is not None:
            update_data["weekly_goal"] = profile_update.weekly_goal
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase.table("user_profiles").update(update_data).eq("user_id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return UserProfile(**response.data[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@router.get("/stats", response_model=UserStats)
async def get_stats(user_id: str):
    """Get user statistics"""
    try:
        response = supabase.table("user_stats").select("*").eq("user_id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            # Create default stats if they don't exist
            default_stats = {
                "user_id": user_id,
                "total_study_hours": 0,
                "courses_completed": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "ai_interactions": 0,
                "study_hours_this_week": 0,
                "last_activity_date": None,
                "week_start_date": datetime.now().date().isoformat()
            }
            create_response = supabase.table("user_stats").insert(default_stats).execute()
            stats_data = create_response.data[0]
        else:
            stats_data = response.data[0]
        
        return UserStats(**stats_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")

@router.get("/achievements", response_model=List[Achievement])
async def get_achievements(user_id: str):
    """Get user achievements with earned status"""
    try:
        # Join user_achievements with achievements table
        response = supabase.table("user_achievements").select(
            "*, achievements(*)"
        ).eq("user_id", user_id).execute()
        
        if not response.data:
            return []
        
        achievements = []
        for item in response.data:
            achievement_data = item.get("achievements", {})
            achievements.append(Achievement(
                id=achievement_data.get("id"),
                title=achievement_data.get("title"),
                description=achievement_data.get("description"),
                icon=achievement_data.get("icon"),
                earned=item.get("earned", False),
                progress=item.get("progress", 0),
                earned_at=item.get("earned_at")
            ))
        
        return achievements
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch achievements: {str(e)}")

# ----- Gamification Endpoints -----

def _xp_needed_for_level(level: int) -> int:
    # XP_needed = 100 * (level ^ 1.5)
    return int(100 * (level ** 1.5))

def _recompute_level(total_xp: int) -> Dict[str, int]:
    level = 1
    while total_xp >= _xp_needed_for_level(level + 1):
        level += 1
    xp_to_next = max(0, _xp_needed_for_level(level + 1) - total_xp)
    return {"current_level": level, "xp_to_next_level": xp_to_next}

@router.post("/award-xp")
async def award_xp(payload: AwardXPRequest):
    try:
        res = supabase.table("user_stats").select("total_xp, current_level, xp_to_next_level").eq("user_id", payload.user_id).maybe_single().execute()
        stats = res.data or {}
        total_xp = int(stats.get("total_xp", 0)) + int(payload.amount)
        level_info = _recompute_level(total_xp)
        supabase.table("user_stats").update({
            "total_xp": total_xp,
            "current_level": level_info["current_level"],
            "xp_to_next_level": level_info["xp_to_next_level"],
            "last_activity_date": datetime.now().date().isoformat()
        }).eq("user_id", payload.user_id).execute()
        supabase.table("xp_events").insert({
            "user_id": payload.user_id,
            "amount": payload.amount,
            "reason": payload.reason or "activity"
        }).execute()
        return {"total_xp": total_xp, **level_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to award XP: {str(e)}")

@router.get("/badges")
async def get_badges(user_id: str):
    try:
        response = supabase.table("user_badges").select("*, badges(*)").eq("user_id", user_id).execute()
        badges = []
        for row in response.data or []:
            b = row.get("badges", {})
            badges.append({
                "id": b.get("id"),
                "name": b.get("name"),
                "description": b.get("description"),
                "icon": b.get("icon"),
                "category": b.get("category"),
                "rarity": b.get("rarity"),
                "earned_at": row.get("earned_at")
            })
        return badges
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch badges: {str(e)}")

@router.post("/unlock-achievement")
async def unlock_achievement(payload: UnlockAchievementRequest):
    try:
        ach = supabase.table("achievements").select("id,xp_reward").eq("id", payload.achievement_id).maybe_single().execute().data
        if not ach:
            raise HTTPException(status_code=404, detail="Achievement not found")
        supabase.table("user_achievements").upsert({
            "user_id": payload.user_id,
            "achievement_id": payload.achievement_id,
            "earned": True,
            "earned_at": datetime.now().isoformat()
        }, on_conflict="user_id,achievement_id").execute()
        # Award XP
        xp_reward = int(ach.get("xp_reward", 0))
        if xp_reward > 0:
            # reuse award flow
            res = supabase.table("user_stats").select("total_xp").eq("user_id", payload.user_id).maybe_single().execute()
            current_xp = int((res.data or {}).get("total_xp", 0))
            total_xp = current_xp + xp_reward
            level_info = _recompute_level(total_xp)
            supabase.table("user_stats").update({
                "total_xp": total_xp,
                "current_level": level_info["current_level"],
                "xp_to_next_level": level_info["xp_to_next_level"]
            }).eq("user_id", payload.user_id).execute()
            supabase.table("xp_events").insert({
                "user_id": payload.user_id,
                "amount": xp_reward,
                "reason": "achievement"
            }).execute()
        return {"success": True, "xp_awarded": xp_reward}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unlock achievement: {str(e)}")

@router.get("/daily-challenges")
async def get_daily_challenges(user_id: str):
    try:
        today = datetime.now().date().isoformat()
        existing = supabase.table("user_challenges").select("*, challenges(*)").eq("user_id", user_id).eq("assigned_date", today).execute()
        if not existing.data:
            # Assign new ones
            try:
                supabase.rpc("assign_daily_challenges", {"p_user": user_id, "p_count": 3}).execute()
            except Exception:
                pass
            existing = supabase.table("user_challenges").select("*, challenges(*)").eq("user_id", user_id).eq("assigned_date", today).execute()
        out = []
        for row in existing.data or []:
            ch = row.get("challenges", {})
            out.append({
                "id": row.get("id"),
                "challenge_id": ch.get("id"),
                "description": ch.get("description"),
                "type": ch.get("type"),
                "requirements": ch.get("requirements"),
                "xp_reward": ch.get("xp_reward"),
                "progress": row.get("progress"),
                "completed": row.get("completed"),
                "assigned_date": row.get("assigned_date")
            })
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch daily challenges: {str(e)}")

@router.post("/complete-challenge")
async def complete_challenge(payload: CompleteChallengeRequest):
    try:
        uc = supabase.table("user_challenges").select("*, challenges(xp_reward)").eq("user_id", payload.user_id).eq("challenge_id", payload.challenge_id).order("assigned_date", desc=True).limit(1).execute()
        if not uc.data:
            raise HTTPException(status_code=404, detail="Challenge not found")
        row = uc.data[0]
        if row.get("completed"):
            return {"success": True, "message": "Already completed"}
        xp_reward = int(((row.get("challenges") or {}).get("xp_reward") or 0))
        supabase.table("user_challenges").update({
            "completed": True,
            "completed_at": datetime.now().isoformat()
        }).eq("id", row["id"]).execute()
        # award xp
        res = supabase.table("user_stats").select("total_xp").eq("user_id", payload.user_id).maybe_single().execute()
        total_xp = int((res.data or {}).get("total_xp", 0)) + xp_reward
        level_info = _recompute_level(total_xp)
        supabase.table("user_stats").update({
            "total_xp": total_xp,
            "current_level": level_info["current_level"],
            "xp_to_next_level": level_info["xp_to_next_level"]
        }).eq("user_id", payload.user_id).execute()
        supabase.table("xp_events").insert({
            "user_id": payload.user_id,
            "amount": xp_reward,
            "reason": "daily_challenge"
        }).execute()
        return {"success": True, "xp_awarded": xp_reward, **level_info}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete challenge: {str(e)}")

@router.post("/avatar")
async def upload_avatar(user_id: str, file: UploadFile = File(...)):
    """Upload user avatar image"""
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, WebP, and GIF are allowed.")
        
        # Validate file size (max 5MB)
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")
        
        # Upload to Supabase Storage
        file_ext = file.filename.split(".")[-1]
        file_path = f"avatars/{user_id}.{file_ext}"
        
        storage_response = supabase.storage.from_("profile-images").upload(
            file_path,
            file_content,
            {"content-type": file.content_type, "upsert": "true"}
        )
        
        # Get public URL
        public_url = supabase.storage.from_("profile-images").get_public_url(file_path)
        
        # Update user profile with new avatar URL
        supabase.table("user_profiles").update({
            "avatar_url": public_url
        }).eq("user_id", user_id).execute()
        
        return {"avatar_url": public_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload avatar: {str(e)}")

@router.post("/stats/increment-study-hours")
async def increment_study_hours(user_id: str, hours: int):
    """Increment study hours for user"""
    try:
        # Get current stats
        response = supabase.table("user_stats").select("*").eq("user_id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="User stats not found")
        
        current_stats = response.data[0]
        
        # Update stats
        update_data = {
            "total_study_hours": current_stats["total_study_hours"] + hours,
            "study_hours_this_week": current_stats["study_hours_this_week"] + hours,
            "last_activity_date": datetime.now().date().isoformat()
        }
        
        supabase.table("user_stats").update(update_data).eq("user_id", user_id).execute()
        
        return {"success": True, "message": f"Added {hours} study hours"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update study hours: {str(e)}")

@router.post("/stats/increment-ai-interactions")
async def increment_ai_interactions(user_id: str):
    """Increment AI interactions count"""
    try:
        response = supabase.table("user_stats").select("ai_interactions").eq("user_id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="User stats not found")
        
        current_count = response.data[0]["ai_interactions"]
        
        supabase.table("user_stats").update({
            "ai_interactions": current_count + 1,
            "last_activity_date": datetime.now().date().isoformat()
        }).eq("user_id", user_id).execute()
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update AI interactions: {str(e)}")

@router.post("/stats/complete-course")
async def complete_course(user_id: str):
    """Mark a course as completed"""
    try:
        response = supabase.table("user_stats").select("courses_completed").eq("user_id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="User stats not found")
        
        current_count = response.data[0]["courses_completed"]
        
        supabase.table("user_stats").update({
            "courses_completed": current_count + 1,
            "last_activity_date": datetime.now().date().isoformat()
        }).eq("user_id", user_id).execute()
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update courses completed: {str(e)}")
