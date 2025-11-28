import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/store/AuthContext";
import { completeChallenge, getDailyChallenges, checkAchievements } from "@/lib/gamificationClient";
import { notifyAchievement, notifyXP } from "./AchievementNotification";
import { CheckCircle2 } from "lucide-react";

interface Challenge {
  id: string;
  challenge_id: string;
  description: string;
  type: string;
  requirements: any;
  xp_reward: number;
  progress: number;
  completed: boolean;
  assigned_date: string;
}

export const DailyChallenges = () => {
  const { user } = useAuth();
  const [items, setItems] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const data: Challenge[] = await getDailyChallenges(user.id);
      setItems(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [user?.id]);

  const onComplete = async (challengeId: string) => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const resp = await completeChallenge(user.id, challengeId);
      if (resp?.xp_awarded) {
        notifyXP(resp.xp_awarded);
      }
      try {
        const chk = await checkAchievements(user.id);
        (chk.unlocked || []).forEach((u: any) => notifyAchievement(u.title, u.xp_reward));
      } catch {}
      await load();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Daily Challenges</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {items.map((c) => (
            <div key={c.id} className={`p-4 rounded-lg border ${c.completed ? "bg-green-50 dark:bg-green-900/20" : "bg-muted/40"}`}>
              <div className="font-semibold">{c.description}</div>
              <div className="text-xs text-muted-foreground mt-1">Reward: {c.xp_reward} XP</div>
              <div className="mt-3">
                {c.completed ? (
                  <div className="inline-flex items-center text-green-600 text-sm">
                    <CheckCircle2 className="w-4 h-4 mr-1" /> Completed
                  </div>
                ) : (
                  <Button size="sm" onClick={() => onComplete(c.challenge_id)} disabled={loading}>Mark Complete</Button>
                )}
              </div>
            </div>
          ))}
          {items.length === 0 && (
            <div className="text-sm text-muted-foreground">No challenges assigned yet.</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
