const BASE = "http://127.0.0.1:8000";

export async function awardXP(userId: string, amount: number, reason?: string) {
  const res = await fetch(`${BASE}/api/profile/award-xp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, amount, reason }),
  });
  if (!res.ok) throw new Error("awardXP failed");
  return res.json();
}

export async function incrementAIInteraction(userId: string) {
  const res = await fetch(`${BASE}/api/profile/stats/increment-ai-interactions?user_id=${userId}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("incrementAIInteraction failed");
  return res.json();
}

export async function checkAchievements(userId: string) {
  const res = await fetch(`${BASE}/api/gamification/check-achievements?user_id=${userId}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("checkAchievements failed");
  return res.json();
}

export async function getDailyChallenges(userId: string) {
  const res = await fetch(`${BASE}/api/profile/daily-challenges?user_id=${userId}`);
  if (!res.ok) throw new Error("getDailyChallenges failed");
  return res.json();
}

export async function completeChallenge(userId: string, challengeId: string) {
  const res = await fetch(`${BASE}/api/profile/complete-challenge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, challenge_id: challengeId }),
  });
  if (!res.ok) throw new Error("completeChallenge failed");
  return res.json();
}

export async function getLeaderboard(scope: "weekly" | "all_time" = "weekly", limit = 100, offset = 0) {
  const res = await fetch(`${BASE}/api/gamification/leaderboard?scope=${scope}&limit=${limit}&offset=${offset}`);
  if (!res.ok) throw new Error("getLeaderboard failed");
  return res.json();
}

export async function getAchievements(userId: string) {
  const res = await fetch(`${BASE}/api/profile/achievements?user_id=${userId}`);
  if (!res.ok) throw new Error("getAchievements failed");
  return res.json();
}

export async function getBadges(userId: string) {
  const res = await fetch(`${BASE}/api/profile/badges?user_id=${userId}`);
  if (!res.ok) throw new Error("getBadges failed");
  return res.json();
}

export async function dailyLogin(userId: string) {
  const res = await fetch(`${BASE}/api/profile/daily-login?user_id=${userId}`, { method: "POST" });
  if (!res.ok) throw new Error("dailyLogin failed");
  return res.json();
}
