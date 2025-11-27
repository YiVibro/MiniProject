import { toast } from "@/components/ui/sonner";

export function notifyXP(amount: number) {
  toast(`+${amount} XP`, { description: "You earned experience points." });
}

export function notifyAchievement(title: string, xpReward?: number) {
  toast(`Achievement Unlocked: ${title}`, {
    description: xpReward ? `+${xpReward} XP` : undefined,
  });
}

export function notifyLevelUp(level: number) {
  toast(`Level Up!`, { description: `You reached level ${level}.` });
}
