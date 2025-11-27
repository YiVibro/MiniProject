import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/store/AuthContext";
import { getAchievements } from "@/lib/gamificationClient";
import { Award } from "lucide-react";

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  earned: boolean;
  progress: number;
  earned_at: string | null;
}

export const AchievementShowcase = () => {
  const { user } = useAuth();
  const [items, setItems] = useState<Achievement[]>([]);

  useEffect(() => {
    let mounted = true;
    (async () => {
      if (!user?.id) return;
      try {
        const data: Achievement[] = await getAchievements(user.id);
        if (mounted) setItems(data);
      } catch {}
    })();
    return () => { mounted = false };
  }, [user?.id]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><Award className="w-5 h-5" />Achievements</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((a) => (
            <div key={a.id} className={`p-4 rounded-lg border ${a.earned ? "bg-primary/5 border-primary/20" : "bg-muted/40"}`}>
              <div className="font-semibold">{a.title}</div>
              <div className="text-sm text-muted-foreground">{a.description}</div>
              <div className="text-xs mt-2">{a.earned ? "Unlocked" : "Locked"}</div>
            </div>
          ))}
          {items.length === 0 && (
            <div className="text-sm text-muted-foreground">No achievements to display yet.</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
