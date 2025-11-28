import { useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useUserProfile } from "./hooks/useUserProfile";
import { XPProgressBar } from "./XPProgressBar";
import { LevelBadge } from "./LevelBadge";
import { AchievementShowcase } from "./AchievementShowcase";
import { DailyChallenges } from "./DailyChallenges";
import { BadgesGallery } from "./BadgesGallery";
import { Leaderboard } from "./Leaderboard";
import { Loader2 } from "lucide-react";

export const GamificationDashboard = () => {
  const { stats, loading, refetch } = useUserProfile();

  useEffect(() => { /* initial load via hook */ }, []);

  if (loading || !stats) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center">
        <div className="flex flex-col items-center gap-2">
          <Loader2 className="w-6 h-6 animate-spin" />
          <div className="text-sm text-muted-foreground">Loading Gamification...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full p-4 sm:p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Gamification</h1>
        <LevelBadge level={stats.current_level ?? 1} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Experience</CardTitle>
        </CardHeader>
        <CardContent>
          <XPProgressBar
            totalXp={stats.total_xp ?? 0}
            currentLevel={stats.current_level ?? 1}
            xpToNextLevel={stats.xp_to_next_level ?? 100}
          />
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <AchievementShowcase />
          <BadgesGallery />
          <DailyChallenges />
        </div>
        <div className="space-y-6">
          <Leaderboard scope="weekly" />
        </div>
      </div>
    </div>
  );
};
