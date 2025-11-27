import React from 'react';
import { LessonDetailView } from './LessonDetailView';

interface LessonContentViewProps {
  lesson: any;
  onComplete: () => void;
  onTakeQuiz: () => void;
  courseProgress?: {
    completed_lessons: number;
    total_lessons: number;
  };
}

export const LessonContentView: React.FC<LessonContentViewProps> = ({
  lesson,
  onComplete,
  onTakeQuiz,
  courseProgress
}) => {
  // Transform lesson data to match LessonDetailView interface
  const transformedLesson = {
    id: lesson.id || lesson.lesson_id || 'unknown',
    title: lesson.title || 'Untitled Lesson',
    content: lesson.metadata?.content || lesson.content || '',
    difficulty: lesson.difficulty || 'intermediate',
    duration: lesson.duration || 45,
    learning_objectives: lesson.metadata?.learning_objectives || lesson.learning_objectives || [],
    prerequisites: lesson.metadata?.prerequisites || lesson.prerequisites || [],
    assessment_questions: lesson.metadata?.questions || lesson.assessment_questions || [],
    practice_exercises: lesson.metadata?.practice_exercises || lesson.practice_exercises || [],
  };

  return (
    <LessonDetailView
      lesson={transformedLesson}
      onComplete={onComplete}
      onStartQuiz={onTakeQuiz}
      courseProgress={courseProgress}
    />
  );
};