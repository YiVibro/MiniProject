// lib/courseService.ts
import api from './api';
import { supabase } from './supabaseClient';

export interface CourseGenerationRequest {
  user_id: string;
  subject: string;
  topic: string;
  duration_weeks: number;
  goal_type: string;
  learning_style: string;
  difficulty: string;
  focus_type: string;
  include_assessments: boolean;
  include_projects: boolean;
  specific_goals: string[];
  description?: string;
}

export interface GeneratedCourse {
  course_id: string;
  title: string;
  subject: string;
  topic: string;
  curriculum: Array<{
    id: string;
    week: number;
    title: string;
    topic: string;
    content: string;
    learning_objectives: string[];
    duration: number;
    type: 'lesson' | 'assessment' | 'project';
    difficulty: string;
    resources: string[];
    practice_exercises: string[];
    questions?: any[];
    passing_score?: number;
    description?: string;
    requirements?: string[];
    deliverables?: string[];
  }>;
  learning_path: {
    path_id: string;
    title: string;
    description: string;
    estimated_duration: number;
    weekly_modules: Array<{
      week: number;
      title: string;
      lessons: any[];
      estimated_duration: number;
    }>;
    total_lessons: number;
    total_assessments: number;
    total_projects: number;
  };
  estimated_duration: number;
  difficulty: string;
  learning_style: string;
  created_at: string;
}

export interface StoredCourse {
  id: string;
  user_id: string;
  course_data: GeneratedCourse;
  title: string;
  subject: string;
  topic: string;
  duration_weeks: number;
  difficulty: string;
  learning_style: string;
  progress_percent: number;
  completed_lessons: string[];
  current_lesson_id: string;
  created_at: string;
  updated_at: string;
}

export class CourseService {
  private baseUrl = '/courses';

  // Generate a new course using AI
  async generateCourse(request: CourseGenerationRequest): Promise<GeneratedCourse> {
    try {
      console.log('Generating course with request:', request);

      // Transform request to match backend's expected format
      const backendRequest = {
        user_id: request.user_id,
        requirements: {
          subject: request.subject,
          topic: request.topic,
          weeks: request.duration_weeks || 4,
          focus: request.focus_type || 'balanced',
          assessments: request.include_assessments !== undefined ? request.include_assessments : true
        }
      };

      console.log('Transformed backend request:', backendRequest);

      // Use the /create endpoint instead of /generate
      const response = await api.post(`${this.baseUrl}/create`, backendRequest);
      console.log('Course generated successfully:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error generating course:', error);
      throw new Error(error.response?.data?.detail || 'Failed to generate course');
    }
  }

  // Save generated course to Supabase
  async saveCourse(userId: string, generatedCourse: GeneratedCourse): Promise<StoredCourse> {
    try {
      const { data, error } = await supabase
        .from('courses')
        .insert([{
          user_id: userId,
          course_data: generatedCourse,
          title: generatedCourse.title,
          subject: generatedCourse.subject,
          topic: generatedCourse.topic,
          duration_weeks: Math.ceil(generatedCourse.estimated_duration / (7 * 60)),
          difficulty: generatedCourse.difficulty,
          learning_style: generatedCourse.learning_style,
          progress_percent: 0,
          completed_lessons: [],
          current_lesson_id: generatedCourse.curriculum[0]?.id || ''
        }])
        .select()
        .single();

      if (error) throw error;
      return data;
    } catch (error: any) {
      console.error('Error saving course:', error);
      throw error;
    }
  }

  // Get all courses for a user
  async getUserCourses(userId: string): Promise<StoredCourse[]> {
    try {
      const { data, error } = await supabase
        .from('courses')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (error) throw error;
      return data || [];
    } catch (error: any) {
      console.error('Error fetching user courses:', error);
      throw error;
    }
  }

  // Update course progress
  async updateCourseProgress(
    courseId: string,
    updates: {
      progress_percent?: number;
      completed_lessons?: string[];
      current_lesson_id?: string;
    }
  ): Promise<void> {
    try {
      const { error } = await supabase
        .from('courses')
        .update(updates)
        .eq('id', courseId);

      if (error) throw error;
    } catch (error: any) {
      console.error('Error updating course progress:', error);
      throw error;
    }
  }

  // Record detailed lesson progress
  async recordLessonProgress(
    userId: string,
    courseId: string,
    lessonId: string,
    data: {
      completed: boolean;
      score?: number;
      time_spent?: number;
    }
  ): Promise<void> {
    try {
      const { error } = await supabase
        .from('user_progress')
        .insert([{
          user_id: userId,
          course_id: courseId,
          lesson_id: lessonId,
          completed: data.completed,
          score: data.score,
          time_spent: data.time_spent,
          completed_at: data.completed ? new Date().toISOString() : null
        }]);

      if (error) throw error;
    } catch (error: any) {
      console.error('Error recording lesson progress:', error);
      throw error;
    }
  }

  // Calculate overall progress for a course
  async calculateCourseProgress(courseId: string): Promise<{ progress: number; completedLessons: string[] }> {
    try {
      // Get all lessons for the course
      const { data: courseData, error: courseError } = await supabase
        .from('courses')
        .select('course_data')
        .eq('id', courseId)
        .single();

      if (courseError) throw courseError;

      // Get completed lessons from progress table
      const { data: progressData, error: progressError } = await supabase
        .from('user_progress')
        .select('lesson_id')
        .eq('course_id', courseId)
        .eq('completed', true);

      if (progressError) throw progressError;

      const totalLessons = courseData.course_data.curriculum.length;
      const completedLessons = progressData?.map(p => p.lesson_id) || [];
      const progress = totalLessons > 0 ? (completedLessons.length / totalLessons) * 100 : 0;

      return {
        progress,
        completedLessons
      };
    } catch (error: any) {
      console.error('Error calculating course progress:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const courseService = new CourseService();
export default courseService;