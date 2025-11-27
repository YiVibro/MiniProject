-- Enhance achievements with categories, tiers, and xp rewards
ALTER TABLE achievements
  ADD COLUMN IF NOT EXISTS category TEXT,
  ADD COLUMN IF NOT EXISTS tier TEXT,
  ADD COLUMN IF NOT EXISTS xp_reward INTEGER DEFAULT 10;

-- Seed expanded achievements (subset representative)
INSERT INTO achievements (title, description, icon, criteria, category, tier, xp_reward) VALUES
  ('First Lesson Complete','Complete your first lesson','BookOpen','{"type":"lessons_completed","count":1}','learning','bronze',10),
  ('10 Lessons Complete','Complete 10 lessons','BookOpen','{"type":"lessons_completed","count":10}','learning','silver',25),
  ('50 Lessons Complete','Complete 50 lessons','BookOpen','{"type":"lessons_completed","count":50}','learning','gold',50),
  ('100 Lessons Complete','Complete 100 lessons','BookOpen','{"type":"lessons_completed","count":100}','learning','platinum',100),
  ('Course Speedrunner','Complete a course in 3 days','Zap','{"type":"course_speed","days":3}','learning','gold',50),
  ('Perfect Score','Score 100% on an assessment','Trophy','{"type":"perfect_score"}','mastery','gold',50),
  ('Study Marathon','Study 5 hours in one day','Clock','{"type":"study_hours_day","hours":5}','learning','gold',50),
  ('3-Day Streak','Maintain a 3-day streak','Calendar','{"type":"streak","count":3}','consistency','bronze',10),
  ('7-Day Streak','Maintain a 7-day streak','Calendar','{"type":"streak","count":7}','consistency','silver',25),
  ('30-Day Streak','Maintain a 30-day streak','Calendar','{"type":"streak","count":30}','consistency','gold',50),
  ('100-Day Streak','Maintain a 100-day streak','Calendar','{"type":"streak","count":100}','consistency','platinum',100),
  ('Early Bird','Study before 8 AM','Sun','{"type":"time_of_day","before":"08:00"}','consistency','silver',25),
  ('Night Owl','Study after 10 PM','Moon','{"type":"time_of_day","after":"22:00"}','consistency','silver',25),
  ('Weekend Warrior','Study on the weekend','Calendar','{"type":"weekday","values":[6,0]}','consistency','bronze',10),
  ('First Question','Ask your first AI question','Brain','{"type":"ai_interactions","count":1}','ai','bronze',10),
  ('10 AI Conversations','Have 10 AI conversations','Brain','{"type":"ai_interactions","count":10}','ai','silver',25),
  ('50 AI Conversations','Have 50 AI conversations','Brain','{"type":"ai_interactions","count":50}','ai','gold',50),
  ('100 AI Conversations','Have 100 AI conversations','Brain','{"type":"ai_interactions","count":100}','ai','platinum',100),
  ('Subject Expert','Complete all courses in a subject','Award','{"type":"subject_complete"}','mastery','platinum',100),
  ('Quiz Master','Complete 50 quizzes','Trophy','{"type":"quizzes_completed","count":50}','mastery','gold',50),
  ('Assessment Ace','Pass 10 assessments with 90%+','Trophy','{"type":"assessments_passed_90","count":10}','mastery','gold',50)
ON CONFLICT DO NOTHING;
