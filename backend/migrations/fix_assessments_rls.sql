-- Fix: Disable RLS on assessments table if it exists
-- This allows the service role to insert/read/update assessments

ALTER TABLE IF EXISTS assessments DISABLE ROW LEVEL SECURITY;

-- Drop any existing RLS policies
DROP POLICY IF EXISTS allow_all ON assessments;

-- Ensure table exists with proper structure
CREATE TABLE IF NOT EXISTS assessments (
    id BIGSERIAL PRIMARY KEY,
    assessment_id TEXT UNIQUE NOT NULL,
    course_id UUID REFERENCES generated_courses(id) ON DELETE CASCADE,
    lesson_id TEXT NOT NULL,
    questions JSONB NOT NULL,
    difficulty TEXT DEFAULT 'medium',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Re-create indexes
CREATE INDEX IF NOT EXISTS idx_assessments_assessment_id ON assessments(assessment_id);
CREATE INDEX IF NOT EXISTS idx_assessments_course_id ON assessments(course_id);
CREATE INDEX IF NOT EXISTS idx_assessments_lesson_id ON assessments(lesson_id);
CREATE INDEX IF NOT EXISTS idx_assessments_created_at ON assessments(created_at);

-- Verify RLS is disabled
ALTER TABLE assessments DISABLE ROW LEVEL SECURITY;
