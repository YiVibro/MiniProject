-- Create assessments table to store assessment questions persistently
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

-- Add indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_assessments_assessment_id ON assessments(assessment_id);
CREATE INDEX IF NOT EXISTS idx_assessments_course_id ON assessments(course_id);
CREATE INDEX IF NOT EXISTS idx_assessments_lesson_id ON assessments(lesson_id);
CREATE INDEX IF NOT EXISTS idx_assessments_created_at ON assessments(created_at);

-- Disable Row Level Security to allow service role access
-- (Supabase service role will handle authentication)
ALTER TABLE assessments DISABLE ROW LEVEL SECURITY;
