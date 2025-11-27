-- Daily and weekly challenges
CREATE TABLE IF NOT EXISTS challenges (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  code TEXT UNIQUE NOT NULL,
  description TEXT NOT NULL,
  type TEXT NOT NULL,
  requirements JSONB NOT NULL,
  xp_reward INTEGER NOT NULL,
  period TEXT NOT NULL CHECK (period IN ('daily','weekly')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_challenges (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  challenge_id UUID NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
  assigned_date DATE NOT NULL,
  progress INTEGER DEFAULT 0,
  completed BOOLEAN DEFAULT FALSE,
  completed_at TIMESTAMPTZ,
  UNIQUE(user_id, challenge_id, assigned_date)
);

ALTER TABLE challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_challenges ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view challenges"
  ON challenges FOR SELECT
  USING (true);

CREATE POLICY "Users can view their user_challenges"
  ON user_challenges FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their user_challenges"
  ON user_challenges FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their user_challenges"
  ON user_challenges FOR UPDATE
  USING (auth.uid() = user_id);

-- Helper function to assign N daily challenges
CREATE OR REPLACE FUNCTION public.assign_daily_challenges(p_user UUID, p_count INTEGER DEFAULT 3)
RETURNS VOID AS $$
BEGIN
  INSERT INTO user_challenges (user_id, challenge_id, assigned_date)
  SELECT p_user, c.id, CURRENT_DATE
  FROM challenges c
  WHERE c.period = 'daily'
    AND NOT EXISTS (
      SELECT 1 FROM user_challenges uc
      WHERE uc.user_id = p_user AND uc.challenge_id = c.id AND uc.assigned_date = CURRENT_DATE
    )
  ORDER BY random()
  LIMIT p_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
