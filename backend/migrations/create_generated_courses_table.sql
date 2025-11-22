-- Migration: Create generated_courses table for storing AI-generated course content
-- This table stores the full curriculum and metadata for courses generated via the continue-learning feature

-- Create generated_courses table
CREATE TABLE IF NOT EXISTS generated_courses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  learning_goal_id UUID REFERENCES learning_goals(id) ON DELETE CASCADE,
  course_name TEXT NOT NULL,
  curriculum JSONB NOT NULL,  -- Full lesson data array
  course_metadata JSONB,  -- Requirements, learning_path, etc.
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_generated_courses_user_id ON generated_courses(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_courses_learning_goal_id ON generated_courses(learning_goal_id);
CREATE INDEX IF NOT EXISTS idx_generated_courses_course_name ON generated_courses(course_name);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_generated_courses_updated_at 
    BEFORE UPDATE ON generated_courses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Alternative: If you prefer to store in learning_goals table instead,
-- you can add these JSONB columns to the learning_goals table:
-- ALTER TABLE learning_goals ADD COLUMN IF NOT EXISTS generated_curriculum JSONB;
-- ALTER TABLE learning_goals ADD COLUMN IF NOT EXISTS course_metadata JSONB;

-- Note: The backend code will automatically try generated_courses first,
-- then fall back to learning_goals JSONB columns if the table doesn't exist.

