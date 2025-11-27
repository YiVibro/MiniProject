from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.database.db import supabase

# Minimal achievement evaluation against available stats
# Supported criteria examples in achievements.criteria JSON:
# {"type":"streak","count":7}
# {"type":"ai_interactions","count":50}
# {"type":"courses_completed","count":10}
# {"type":"study_hours_day","hours":5}
# Unsupported placeholders are ignored safely.

def _fetch_user_stats(user_id: str) -> Dict[str, Any]:
    res = supabase.table("user_stats").select("*").eq("user_id", user_id).maybe_single().execute()
    return res.data or {}


def _meets_criterion(stats: Dict[str, Any], criterion: Dict[str, Any]) -> bool:
    ctype = (criterion or {}).get("type")
    if not ctype:
        return False

    if ctype == "streak":
        required = int(criterion.get("count", 0))
        return int(stats.get("current_streak", 0)) >= required

    if ctype == "ai_interactions":
        required = int(criterion.get("count", 0))
        return int(stats.get("ai_interactions", 0)) >= required

    if ctype == "courses_completed":
        required = int(criterion.get("count", 0))
        return int(stats.get("courses_completed", 0)) >= required

    if ctype == "study_hours_day":
        # This requires tracking per-day hours; fall back to total hours heuristic
        hours = int(criterion.get("hours", 0))
        # If total weekly hours >= daily target, allow unlock (approximation)
        return int(stats.get("study_hours_this_week", 0)) >= hours

    # Unsupported: lessons_completed, quizzes_completed, perfect_score, course_speed, etc.
    return False


def _recompute_level(total_xp: int) -> Dict[str, int]:
    def xp_needed(level: int) -> int:
        return int(100 * (level ** 1.5))
    level = 1
    while total_xp >= xp_needed(level + 1):
        level += 1
    xp_to_next = max(0, xp_needed(level + 1) - total_xp)
    return {"current_level": level, "xp_to_next_level": xp_to_next}


def _award_xp(user_id: str, amount: int, reason: str) -> None:
    res = supabase.table("user_stats").select("total_xp").eq("user_id", user_id).maybe_single().execute()
    current_xp = int((res.data or {}).get("total_xp", 0))
    total_xp = current_xp + int(amount)
    level_info = _recompute_level(total_xp)
    supabase.table("user_stats").update({
        "total_xp": total_xp,
        "current_level": level_info["current_level"],
        "xp_to_next_level": level_info["xp_to_next_level"],
        "last_activity_date": datetime.now().date().isoformat()
    }).eq("user_id", user_id).execute()
    supabase.table("xp_events").insert({
        "user_id": user_id,
        "amount": int(amount),
        "reason": reason,
    }).execute()


def check_and_unlock_achievements(user_id: str) -> List[Dict[str, Any]]:
    """Evaluate all achievements for the user, unlock eligible ones, and award XP."""
    stats = _fetch_user_stats(user_id)
    if not stats:
        return []

    # Fetch all user_achievements joined with achievements
    resp = supabase.table("user_achievements").select("*,achievements(*)").eq("user_id", user_id).execute()
    rows = resp.data or []

    unlocked: List[Dict[str, Any]] = []
    for row in rows:
        if row.get("earned"):
            continue
        ach = row.get("achievements") or {}
        criterion = ach.get("criteria")
        if _meets_criterion(stats, criterion):
            # Unlock
            supabase.table("user_achievements").update({
                "earned": True,
                "earned_at": datetime.now().isoformat()
            }).eq("id", row.get("id")).execute()
            xp_reward = int(ach.get("xp_reward") or 0)
            if xp_reward > 0:
                _award_xp(user_id, xp_reward, "achievement")
            unlocked.append({
                "achievement_id": ach.get("id"),
                "title": ach.get("title"),
                "xp_reward": xp_reward,
            })

    return unlocked
