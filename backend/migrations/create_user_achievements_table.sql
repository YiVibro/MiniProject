-- Migration: Create user_achievements table for gamification
-- This table stores achievement definitions and user progress

-- Create achievements table (master list of all achievements)
CREATE TABLE IF NOT EXISTS achievements (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  icon TEXT NOT NULL, -- Icon name from lucide-react
  criteria JSONB NOT NULL, -- JSON defining unlock criteria
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user_achievements table (tracks which users earned which achievements)
CREATE TABLE IF NOT EXISTS user_achievements (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  achievement_id UUID NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
  earned BOOLEAN DEFAULT FALSE,
  progress INTEGER DEFAULT 0, -- For progressive achievements
  earned_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, achievement_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_achievement_id ON user_achievements(achievement_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_earned ON user_achievements(earned);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_user_achievements_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    IF NEW.earned = TRUE AND OLD.earned = FALSE THEN
      NEW.earned_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_achievements_updated_at_trigger
    BEFORE UPDATE ON user_achievements
    FOR EACH ROW
    EXECUTE FUNCTION update_user_achievements_updated_at();

-- Enable Row Level Security
ALTER TABLE achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_achievements ENABLE ROW LEVEL SECURITY;

-- RLS Policies for achievements (everyone can read achievement definitions)
CREATE POLICY "Anyone can view achievements"
  ON achievements FOR SELECT
  USING (true);

-- RLS Policies for user_achievements
CREATE POLICY "Users can view their own achievements"
  ON user_achievements FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own achievements"
  ON user_achievements FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own achievements"
  ON user_achievements FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Insert default achievements
INSERT INTO achievements (title, description, icon, criteria) VALUES
  ('First Goal Completed', 'Completed your first learning goal', 'Target', '{"type": "goals_completed", "count": 1}'),
  ('Study Streak', 'Studied for 7 consecutive days', 'Calendar', '{"type": "streak", "count": 7}'),
  ('AI Assistant Pro', 'Had 50+ conversations with AI tutor', 'Brain', '{"type": "ai_interactions", "count": 50}'),
  ('Knowledge Master', 'Completed 10 courses', 'BookOpen', '{"type": "courses_completed", "count": 10}'),
  ('Speed Learner', 'Completed a course in under 2 weeks', 'Zap', '{"type": "course_speed", "days": 14}')
ON CONFLICT DO NOTHING;

-- Function to auto-create user achievement records when user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user_achievements()
RETURNS TRIGGER AS $$
BEGIN
  -- Create user_achievement records for all existing achievements
  INSERT INTO public.user_achievements (user_id, achievement_id, earned, progress)
  SELECT NEW.id, id, FALSE, 0
  FROM public.achievements;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to auto-create achievement records when user signs up
DROP TRIGGER IF EXISTS on_auth_user_created_achievements ON auth.users;
CREATE TRIGGER on_auth_user_created_achievements
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user_achievements();
