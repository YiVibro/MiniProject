/**
 * Dynamic Course Service
 * =====================
 * 
 * Service for creating dynamic courses using the new_agent system
 */

import api from './api';

export interface CourseRequest {
  subject: string;
  topic: string;
  difficulty?: string;
  duration_weeks?: number;
  user_profile?: {
    user_id: string;
    name: string;
    email: string;
    learning_goals?: string[];
    interests?: string[];
  };
  learning_style?: string;
  available_time?: number;
}

export interface LessonRequest {
  subject: string;
  topic: string;
  difficulty?: string;
  user_profile?: {
    user_id: string;
    name: string;
    email: string;
    learning_goals?: string[];
    interests?: string[];
  };
  learning_style?: string;
  duration?: number;
}

export interface CourseResponse {
  course_id: string;
  title: string;
  curriculum: Array<{
    id: string;
    title: string;
    difficulty: string;
    duration: number;
    subtopics: Array<{
      title: string;
      deadline_minutes: number;
    }>;
    questions: Array<{
      id: string;
      question: string;
      type: string;
      options?: Array<{
        text: string;
        correct: boolean;
      }>;
    }>;
  }>;
  learning_path: {
    title: string;
    description: string;
  };
  total_lessons: number;
  estimated_duration: number;
}

export interface LessonResponse {
  lesson_id: string;
  title: string;
  content: string;
  difficulty: string;
  duration: number;
  learning_objectives: string[];
  prerequisites: string[];
  assessment_questions: Array<{
    question: string;
    type: string;
    options?: string[];
    correct_answer?: string;
    explanation?: string;
  }>;
  practice_exercises: string[];
}

export interface SubjectOption {
  value: string;
  label: string;
}

export interface DifficultyLevel {
  value: string;
  label: string;
}

export interface LearningStyle {
  value: string;
  label: string;
}

class DynamicCourseService {
  private baseUrl = '/api/dynamic-course';

  /**
   * Create a dynamic course using the new_agent system
   */
  async createCourse(request: CourseRequest): Promise<CourseResponse> {
    try {
      const response = await api.post(`${this.baseUrl}/create-course`, request);
      return response.data;
    } catch (error: any) {
      console.error('Error creating dynamic course:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create dynamic course');
    }
  }

  /**
   * Create a single dynamic lesson using the new_agent system
   */
  async createLesson(request: LessonRequest): Promise<LessonResponse> {
    try {
      const response = await api.post(`${this.baseUrl}/create-lesson`, request);
      return response.data;
    } catch (error: any) {
      console.error('Error creating dynamic lesson:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create dynamic lesson');
    }
  }

  /**
   * Get available subjects for course creation
   */
  async getSubjects(): Promise<string[]> {
    try {
      const response = await api.get(`${this.baseUrl}/subjects`);
      return response.data.subjects;
    } catch (error: any) {
      console.error('Error fetching subjects:', error);
      return [
        'Mathematics',
        'Physics',
        'Chemistry',
        'Biology',
        'Computer Science',
        'Programming',
        'Data Science',
        'Machine Learning',
        'Web Development',
        'Mobile Development',
        'Artificial Intelligence',
        'Cybersecurity',
        'Business',
        'Economics',
        'History',
        'Literature',
        'Languages',
        'Psychology',
        'Philosophy',
        'Art',
        'Music'
      ];
    }
  }

  /**
   * Get available difficulty levels
   */
  async getDifficultyLevels(): Promise<DifficultyLevel[]> {
    try {
      const response = await api.get(`${this.baseUrl}/difficulty-levels`);
      return response.data.levels;
    } catch (error: any) {
      console.error('Error fetching difficulty levels:', error);
      return [
        { value: 'beginner', label: 'Beginner' },
        { value: 'intermediate', label: 'Intermediate' },
        { value: 'advanced', label: 'Advanced' },
        { value: 'expert', label: 'Expert' }
      ];
    }
  }

  /**
   * Get available learning styles
   */
  async getLearningStyles(): Promise<LearningStyle[]> {
    try {
      const response = await api.get(`${this.baseUrl}/learning-styles`);
      return response.data.styles;
    } catch (error: any) {
      console.error('Error fetching learning styles:', error);
      return [
        { value: 'visual', label: 'Visual' },
        { value: 'auditory', label: 'Auditory' },
        { value: 'kinesthetic', label: 'Kinesthetic' },
        { value: 'reading_writing', label: 'Reading/Writing' },
        { value: 'analytical', label: 'Analytical' },
        { value: 'practical', label: 'Practical' },
        { value: 'balanced', label: 'Balanced' }
      ];
    }
  }

  /**
   * Create a course with user profile from auth context
   */
  async createCourseWithUser(
    subject: string,
    topic: string,
    difficulty: string = 'medium',
    duration_weeks: number = 4,
    user: any
  ): Promise<CourseResponse> {
    const request: CourseRequest = {
      subject,
      topic,
      difficulty,
      duration_weeks,
      user_profile: {
        user_id: user.id,
        name: user.user_metadata?.full_name || 'User',
        email: user.email,
        learning_goals: [],
        interests: []
      },
      learning_style: 'balanced',
      available_time: 60
    };

    return this.createCourse(request);
  }

  /**
   * Create a lesson with user profile from auth context
   */
  async createLessonWithUser(
    subject: string,
    topic: string,
    difficulty: string = 'medium',
    user: any
  ): Promise<LessonResponse> {
    const request: LessonRequest = {
      subject,
      topic,
      difficulty,
      user_profile: {
        user_id: user.id,
        name: user.user_metadata?.full_name || 'User',
        email: user.email,
        learning_goals: [],
        interests: []
      },
      learning_style: 'balanced',
      duration: 45
    };

    return this.createLesson(request);
  }
}

export const dynamicCourseService = new DynamicCourseService();
export default dynamicCourseService;
