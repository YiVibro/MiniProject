-- Migration: Create user_stats table for tracking study metrics
-- This table stores statistics about user learning activities

-- Create user_stats table
CREATE TABLE IF NOT EXISTS user_stats (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  total_study_hours INTEGER DEFAULT 0,
  courses_completed INTEGER DEFAULT 0,
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  ai_interactions INTEGER DEFAULT 0,
  last_activity_date DATE,
  study_hours_this_week INTEGER DEFAULT 0,
  week_start_date DATE,
  total_xp INTEGER DEFAULT 0,
  current_level INTEGER DEFAULT 1,
  xp_to_next_level INTEGER DEFAULT 100,
  total_points INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_user_stats_user_id ON user_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_user_stats_last_activity ON user_stats(last_activity_date);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_user_stats_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_stats_updated_at_trigger
    BEFORE UPDATE ON user_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_user_stats_updated_at();

-- Enable Row Level Security
ALTER TABLE user_stats ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only read and update their own stats
CREATE POLICY "Users can view their own stats"
  ON user_stats FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own stats"
  ON user_stats FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own stats"
  ON user_stats FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Function to auto-create stats on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user_stats()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_stats (user_id, week_start_date)
  VALUES (NEW.id, CURRENT_DATE - EXTRACT(DOW FROM CURRENT_DATE)::INTEGER);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to auto-create stats when user signs up
DROP TRIGGER IF EXISTS on_auth_user_created_stats ON auth.users;
CREATE TRIGGER on_auth_user_created_stats
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user_stats();

-- Function to update weekly stats (reset on new week)
CREATE OR REPLACE FUNCTION public.check_and_reset_weekly_stats()
RETURNS TRIGGER AS $$
DECLARE
  current_week_start DATE;
BEGIN
  current_week_start := CURRENT_DATE - EXTRACT(DOW FROM CURRENT_DATE)::INTEGER;
  
  -- If we're in a new week, reset weekly stats
  IF NEW.week_start_date < current_week_start THEN
    NEW.study_hours_this_week := 0;
    NEW.week_start_date := current_week_start;
  END IF;
  
  -- Update streak logic
  IF NEW.last_activity_date IS NOT NULL THEN
    IF CURRENT_DATE - NEW.last_activity_date = 1 THEN
      -- Consecutive day, increment streak
      NEW.current_streak := NEW.current_streak + 1;
      IF NEW.current_streak > NEW.longest_streak THEN
        NEW.longest_streak := NEW.current_streak;
      END IF;
    ELSIF CURRENT_DATE > NEW.last_activity_date + 1 THEN
      -- Streak broken
      NEW.current_streak := 1;
    END IF;
  ELSE
    -- First activity
    NEW.current_streak := 1;
    NEW.longest_streak := 1;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_weekly_stats_trigger
  BEFORE UPDATE ON user_stats
  FOR EACH ROW
  EXECUTE FUNCTION public.check_and_reset_weekly_stats();
