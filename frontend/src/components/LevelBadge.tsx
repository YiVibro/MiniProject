import { cn } from "@/lib/utils";

interface LevelBadgeProps {
  level: number;
}

const levelTitle = (lvl: number) => {
  if (lvl <= 5) return "Novice Learner";
  if (lvl <= 10) return "Eager Student";
  if (lvl <= 15) return "Dedicated Scholar";
  if (lvl <= 20) return "Knowledge Seeker";
  if (lvl <= 30) return "Learning Expert";
  if (lvl <= 40) return "Master Student";
  if (lvl <= 50) return "Learning Legend";
  return "Grandmaster";
};

export const LevelBadge = ({ level }: LevelBadgeProps) => {
  return (
    <div className={cn("inline-flex items-center gap-3 px-4 py-2 rounded-full border shadow-sm bg-background")}> 
      <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-white flex items-center justify-center font-bold">
        {level}
      </div>
      <div className="flex flex-col">
        <span className="text-sm font-semibold">{levelTitle(level)}</span>
        <span className="text-xs text-muted-foreground">Level {level}</span>
      </div>
    </div>
  );
};
