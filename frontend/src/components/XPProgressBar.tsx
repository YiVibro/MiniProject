import { motion } from "framer-motion";

interface XPProgressBarProps {
  totalXp: number;
  currentLevel: number;
  xpToNextLevel: number;
}

export const XPProgressBar = ({ totalXp, currentLevel, xpToNextLevel }: XPProgressBarProps) => {
  const nextLevelTotal = totalXp + xpToNextLevel;
  const progress = nextLevelTotal > 0 ? (totalXp / nextLevelTotal) * 100 : 0;

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span>Level {currentLevel}</span>
        <span>{totalXp} XP</span>
      </div>
      <motion.div initial={{ width: 0 }} animate={{ width: "100%" }} transition={{ duration: 0.8 }}>
        <div className="h-2 w-full bg-muted rounded">
          <div
            className="h-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded"
            style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
          />
        </div>
      </motion.div>
      <p className="text-xs text-muted-foreground">{xpToNextLevel} XP to next level</p>
    </div>
  );
}
