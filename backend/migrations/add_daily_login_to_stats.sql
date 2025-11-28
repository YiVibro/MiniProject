-- Add column to track daily login reward claim
ALTER TABLE user_stats
  ADD COLUMN IF NOT EXISTS last_daily_login_reward DATE;
