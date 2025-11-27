import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getLeaderboard } from "@/lib/gamificationClient";

interface Row {
  user_id: string;
  rank: number;
  total_xp?: number;
  weekly_xp?: number;
  name?: string | null;
  avatar_url?: string | null;
}

export const Leaderboard = ({ scope = "weekly" as "weekly" | "all_time" }) => {
  const [rows, setRows] = useState<Row[]>([]);
  const [active, setActive] = useState<"weekly" | "all_time">(scope);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const data = await getLeaderboard(active);
        if (mounted) setRows(data.results || []);
      } catch {}
    })();
    return () => { mounted = false };
  }, [active]);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Leaderboard</CardTitle>
          <div className="flex gap-2 text-sm">
            <button className={`px-3 py-1 rounded ${active === "weekly" ? "bg-primary text-primary-foreground" : "bg-muted"}`} onClick={() => setActive("weekly")}>Weekly</button>
            <button className={`px-3 py-1 rounded ${active === "all_time" ? "bg-primary text-primary-foreground" : "bg-muted"}`} onClick={() => setActive("all_time")}>All-time</button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-muted-foreground">
              <tr>
                <th className="text-left p-2">Rank</th>
                <th className="text-left p-2">User</th>
                <th className="text-left p-2">XP</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(r => (
                <tr key={`${r.user_id}-${r.rank}`} className="border-t">
                  <td className="p-2">{r.rank}</td>
                  <td className="p-2 flex items-center gap-2">
                    {r.avatar_url && <img src={r.avatar_url} className="w-6 h-6 rounded-full" />}
                    <span>{r.name || r.user_id.slice(0, 6)}</span>
                  </td>
                  <td className="p-2">{active === "weekly" ? r.weekly_xp ?? 0 : r.total_xp ?? 0}</td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr><td className="p-2 text-muted-foreground" colSpan={3}>No data yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
