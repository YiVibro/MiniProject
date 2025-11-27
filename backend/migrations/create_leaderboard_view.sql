-- XP events for leaderboards and audits
CREATE TABLE IF NOT EXISTS xp_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  amount INTEGER NOT NULL,
  reason TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE xp_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their xp events"
  ON xp_events FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their xp events"
  ON xp_events FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Leaderboard views
CREATE OR REPLACE VIEW leaderboard_all_time AS
SELECT
  us.user_id,
  us.total_xp,
  RANK() OVER (ORDER BY us.total_xp DESC, us.updated_at ASC) AS rank
FROM user_stats us;

CREATE OR REPLACE VIEW leaderboard_weekly AS
SELECT
  e.user_id,
  COALESCE(SUM(e.amount),0) AS weekly_xp,
  RANK() OVER (ORDER BY COALESCE(SUM(e.amount),0) DESC) AS rank
FROM xp_events e
WHERE e.created_at >= date_trunc('week', now())
GROUP BY e.user_id;
