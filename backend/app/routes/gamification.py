from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from app.database.db import supabase
from datetime import datetime

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


def _xp_needed_for_level(level: int) -> int:
    return int(100 * (level ** 1.5))


def _level_title(level: int) -> str:
    if 1 <= level <= 5:
        return "Novice Learner"
    if 6 <= level <= 10:
        return "Eager Student"
    if 11 <= level <= 15:
        return "Dedicated Scholar"
    if 16 <= level <= 20:
        return "Knowledge Seeker"
    if 21 <= level <= 30:
        return "Learning Expert"
    if 31 <= level <= 40:
        return "Master Student"
    if 41 <= level <= 50:
        return "Learning Legend"
    return "Grandmaster"


@router.get("/level-info")
async def level_info(max_level: int = 50):
    levels = []
    for lvl in range(1, max(1, min(200, max_level)) + 1):
        levels.append({
            "level": lvl,
            "xp_required": _xp_needed_for_level(lvl),
            "title": _level_title(lvl),
        })
    return {"levels": levels}


@router.get("/leaderboard")
async def leaderboard(scope: str = "weekly", limit: int = 100, offset: int = 0):
    try:
        if scope not in ("weekly", "all_time"):
            raise HTTPException(status_code=400, detail="Invalid scope")
        res = supabase.rpc("get_leaderboard", {"p_scope": scope, "p_limit": limit, "p_offset": offset}).execute()
        rows = res.data or []
        return {"scope": scope, "results": rows}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load leaderboard: {str(e)}")


@router.get("/user-rank")
async def user_rank(user_id: str, scope: str = "weekly"):
    try:
        if scope not in ("weekly", "all_time"):
            raise HTTPException(status_code=400, detail="Invalid scope")
        res = supabase.rpc("get_user_rank", {"p_user": user_id, "p_scope": scope}).execute()
        data = (res.data or [{}])[0]
        return {
            "user_id": user_id,
            "rank": data.get("rank"),
            "weekly_xp": data.get("weekly_xp"),
            "total_xp": data.get("total_xp"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load user rank: {str(e)}")


@router.post("/check-achievements")
async def check_achievements(user_id: str):
    try:
        from app.utils.achievement_triggers import check_and_unlock_achievements
        unlocked = check_and_unlock_achievements(user_id)
        return {"unlocked": unlocked}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check achievements: {str(e)}")
