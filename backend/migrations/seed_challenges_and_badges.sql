-- Ensure required tables exist (idempotent)
CREATE TABLE IF NOT EXISTS badges (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT UNIQUE NOT NULL,
  description TEXT NOT NULL,
  icon TEXT NOT NULL,
  category TEXT NOT NULL,
  rarity TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_badges (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  badge_id UUID NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
  earned_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb,
  UNIQUE(user_id, badge_id)
);

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

-- Seed default daily challenges and badges

-- Seed challenges (daily)
INSERT INTO challenges (code, description, type, requirements, xp_reward, period)
VALUES
  ('daily_study_30', 'Study for 30 minutes today', 'study_time', '{"minutes":30}'::jsonb, 25, 'daily'),
  ('daily_study_60', 'Study for 60 minutes today', 'study_time', '{"minutes":60}'::jsonb, 40, 'daily'),
  ('daily_lessons_2', 'Complete 2 lessons today', 'lessons', '{"count":2}'::jsonb, 30, 'daily'),
  ('daily_quizzes_1', 'Take 1 quiz today', 'quizzes', '{"count":1}'::jsonb, 25, 'daily'),
  ('daily_ai_5', 'Ask 5 questions to AI today', 'ai_questions', '{"count":5}'::jsonb, 30, 'daily'),
  ('daily_streak', 'Maintain your streak today', 'streak', '{"maintain":true}'::jsonb, 20, 'daily')
ON CONFLICT DO NOTHING;

-- Seed badges
INSERT INTO badges (name, description, icon, category, rarity)
VALUES
  ('Course Completer', 'Complete any course', 'Award', 'learning', 'common'),
  ('Quiz Champion', 'Finish 10 quizzes', 'Trophy', 'learning', 'uncommon'),
  ('Assessment Master', 'Pass 5 assessments with 90%+', 'Medal', 'mastery', 'rare'),
  ('Study Streaker', 'Maintain a 7-day streak', 'Calendar', 'consistency', 'uncommon'),
  ('Early Adopter', 'Among the first 100 users', 'Sparkles', 'special', 'epic'),
  ('Beta Tester', 'Helped test new features', 'FlaskConical', 'special', 'epic')
ON CONFLICT DO NOTHING;
