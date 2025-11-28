import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/store/AuthContext";
import { getBadges } from "@/lib/gamificationClient";

interface BadgeItem {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  rarity: string;
  earned_at?: string | null;
}

export const BadgesGallery = () => {
  const { user } = useAuth();
  const [items, setItems] = useState<BadgeItem[]>([]);

  useEffect(() => {
    let mounted = true;
    (async () => {
      if (!user?.id) return;
      try {
        const data: BadgeItem[] = await getBadges(user.id);
        if (mounted) setItems(data);
      } catch {}
    })();
    return () => { mounted = false };
  }, [user?.id]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Badges</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map(b => (
            <div key={b.id} className={`p-4 rounded-lg border relative ${b.earned_at ? "bg-primary/5 border-primary/20" : "bg-muted/40"}`}>
              <div className="font-semibold">{b.name}</div>
              <div className="text-xs text-muted-foreground">{b.category} • {b.rarity}</div>
              <div className="text-sm text-muted-foreground mt-1">{b.description}</div>
              {!b.earned_at && (
                <div className="absolute inset-0 rounded-lg bg-background/50 backdrop-blur-[1px] flex items-center justify-center text-xs text-muted-foreground">
                  Locked
                </div>
              )}
            </div>
          ))}
          {items.length === 0 && (
            <div className="text-sm text-muted-foreground">No badges defined yet.</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
