// agentService.ts
import api from './api';

export interface CreateLearningPlanRequest {
  user_id: string;
  user_request: string;
  preferences?: Record<string, any>;
}

export interface LearningPlanResponse {
  path_id: string;
  requirements: Record<string, any>;
  curriculum: Array<{
    id: string;
    title: string;
    difficulty: string;
    duration: number;
    content: string;
    learning_objectives: string[];
    prerequisites: string[];
  }>;
  timeline: string;
  goals: string[];
}

export interface CreateCourseRequest {
  user_id: string;
  subject: string;
  topic: string;
  weeks: number;
  focus: string;
  assessments: boolean;
  user_profile: {
    name: string;
    email: string;
    learning_style: string;
    preferred_difficulty: string;
    available_time: number;
    learning_goals: string[];
    interests: string[];
  };
}

export interface CourseResponse {
  course_id: string;
  curriculum: Array<{
    id: string;
    title: string;
    difficulty: string;
    duration: number;
    content: string;
    learning_objectives: string[];
    prerequisites: string[];
    subtopics?: Array<{ title: string; deadline_minutes: number }>;
    questions?: Array<{
      question: string;
      type: 'multiple_choice' | 'short_answer';
      options: string[];
      answer: string;
    }>;
  }>;
  learning_path: {
    path_id: string;
    title: string;
    description: string;
    estimated_duration: number;
    difficulty_progression: string[];
    milestones: string[];
  };
  requirements: {
    subject: string;
    topic: string;
    weeks: number;
    focus: string;
    assessments: boolean;
  };
}

export interface ProgressTrackingRequest {
  user_id: string;
  activity: string;
  data: Record<string, any>;
}

export interface ProgressResponse {
  progress: Record<string, any>;
  plan_status: Record<string, any>;
  recommendations: string[];
}

export interface LearningSessionRequest {
  user_id: string;
  lesson_id: string;
  session_preferences?: Record<string, any>;
}

export interface LearningSessionResponse {
  session_id: string;
  lesson: {
    id: string;
    title: string;
    content: string;
    difficulty: string;
    duration: number;
    learning_objectives: string[];
    prerequisites: string[];
  };
  adaptive_content: Record<string, any>;
  recommendations: string[];
}

export interface LearningStyle {
  value: string;
  label: string;
  description: string;
}

export interface DifficultyLevel {
  value: string;
  label: string;
  description: string;
}

// Assessment-related interfaces
export interface CreateAssessmentRequest {
  lesson_id: string;
  difficulty?: string;
  num_questions?: number;
  question_types?: string[];
}

export interface AssessmentResponse {
  assessment_id: string;
  questions: Array<{
    id: string;
    question: string;
    type: 'multiple_choice' | 'true_false' | 'short_answer';
    options?: string[];
    correct_answer: string;
    explanation?: string;
  }>;
  time_limit: number;
  passing_score: number;
}

export interface EvaluateAssessmentRequest {
  assessment_id: string;
  user_answers: Record<string, any>;
  user_id: string;
}

export interface EvaluateAssessmentResponse {
  score: number;
  passed: boolean;
  gaps: Array<{
    concept: string;
    severity: 'low' | 'medium' | 'high';
    description: string;
    remedial_suggestions: string[];
  }>;
  remedial_content: {
    title: string;
    content: string;
    resources: string[];
  };
  next_steps: string[];
}

// Learning Path interfaces
export interface LearningPathNode {
  id: string;
  type: 'lesson' | 'practice' | 'assessment' | 'remedial';
  title: string;
  description: string;
  status: 'locked' | 'unlocked' | 'completed' | 'current';
  duration: number;
  difficulty: string;
  prerequisites?: string[];
  metadata?: Record<string, any>;
}

export interface LearningPathData {
  path_id: string;
  title: string;
  description: string;
  nodes: LearningPathNode[];
  current_node_id: string;
  progress_percentage: number;
  estimated_total_duration: number;
}

export class AgentService {
  private baseUrl = '/agents';

  // Learning Plan Management
  async createLearningPlan(request: CreateLearningPlanRequest): Promise<LearningPlanResponse> {
    try {
      console.log('Creating learning plan with request:', request);
      const response = await api.post(`${this.baseUrl}/create-learning-plan`, request);
      console.log('Learning plan created:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error creating learning plan:', error);
      throw error;
    }
  }

  async getLearningPlanStatus(userId: string): Promise<Record<string, any>> {
    try {
      console.log('Calling learning-plan-status for user:', userId);
      const response = await api.get(`${this.baseUrl}/learning-plan-status/${userId}`);
      console.log('Learning plan status response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error getting learning plan status:', error);
      if (error.response?.status === 404) {
        // Learning plan doesn't exist yet - this is normal for new users
        console.log('No learning plan found for user, returning empty state');
        return {
          progress: 0,
          curriculum: [],
          title: 'New Learning Path',
          description: 'Your learning journey will be created as you progress'
        };
      }
      throw error;
    }
  }

  // Course Creation
  async createCourse(request: CreateCourseRequest): Promise<CourseResponse> {
    try {
      console.log('Creating course with request:', request);
      const response = await api.post(`${this.baseUrl}/create-course`, request);
      console.log('Course created:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error creating course:', error);
      throw error;
    }
  }

  async getCourse(courseId: string): Promise<CourseResponse> {
    try {
      console.log('Getting course:', courseId);
      const response = await api.get(`${this.baseUrl}/course/${courseId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error getting course:', error);
      throw error;
    }
  }

  // Progress Tracking
  async trackProgress(request: ProgressTrackingRequest): Promise<ProgressResponse> {
    try {
      console.log('Tracking progress:', request);
      const response = await api.post(`${this.baseUrl}/track-progress`, request);
      return response.data;
    } catch (error: any) {
      console.error('Error tracking progress:', error);
      throw error;
    }
  }

  // Learning Sessions
  async startLearningSession(request: LearningSessionRequest): Promise<LearningSessionResponse> {
    try {
      console.log('Starting learning session:', request);
      const response = await api.post(`${this.baseUrl}/start-learning-session`, request);
      console.log('Learning session started:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error starting learning session:', error);
      throw error;
    }
  }

  async processUserInteraction(
    sessionId: string,
    interactionType: string,
    interactionData: Record<string, any>
  ): Promise<Record<string, any>> {
    try {
      console.log('Processing user interaction:', { sessionId, interactionType, interactionData });
      const response = await api.post(`${this.baseUrl}/process-interaction`, {
        session_id: sessionId,
        interaction_type: interactionType,
        interaction_data: interactionData
      });
      return response.data;
    } catch (error: any) {
      console.error('Error processing user interaction:', error);
      throw error;
    }
  }

  async endLearningSession(sessionId: string): Promise<Record<string, any>> {
    try {
      console.log('Ending learning session:', sessionId);
      const response = await api.post(`${this.baseUrl}/end-learning-session/${sessionId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error ending learning session:', error);
      throw error;
    }
  }

  // Assessment System
  async createAssessment(request: CreateAssessmentRequest): Promise<AssessmentResponse> {
    try {
      console.log('Creating assessment:', request);
      const response = await api.post(`${this.baseUrl}/create-assessment`, request);
      console.log('Assessment created:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error creating assessment:', error);
      // Return mock assessment if backend is not available
      console.log('Returning mock assessment as fallback');
      return this.getMockAssessment(request.lesson_id);
    }
  }

  async evaluateAssessment(request: EvaluateAssessmentRequest): Promise<EvaluateAssessmentResponse> {
    try {
      console.log('Evaluating assessment:', request);
      const response = await api.post(`${this.baseUrl}/evaluate-assessment`, request);
      return response.data;
    } catch (error: any) {
      console.error('Error evaluating assessment:', error);
      // Return mock evaluation if backend is not available
      console.log('Returning mock evaluation as fallback');
      return this.getMockEvaluation(request);
    }
  }

  // Learning Path Management
  async getLearningPath(userId: string, courseId: string): Promise<LearningPathData> {
    console.log('getLearningPath called with:', { userId, courseId });
    
    if (!userId) {
      console.error('User ID is required to get learning path');
      throw new Error('User ID is required to get learning path');
    }
    
    if (!courseId) {
      console.error('Course ID is required to get learning path');
      throw new Error('Course ID is required to get learning path');
    }

    try {
      // First try to get the existing learning plan status
      let progressResponse;
      try {
        progressResponse = await this.getLearningPlanStatus(userId);
        console.log('Progress response:', progressResponse);
      } catch (error) {
        console.log('No existing learning plan, creating new one...');
        // If no learning plan exists, create a basic one
        progressResponse = {
          title: 'Dynamic Learning Path',
          description: 'Your personalized learning journey',
          progress: 0,
          curriculum: []
        };
      }

      // Transform backend data into learning path nodes
      const nodes: LearningPathNode[] = this.transformToLearningPath(progressResponse);
      console.log('Transformed nodes:', nodes);

      // If no nodes were created, use default nodes
      const finalNodes = nodes.length > 0 ? nodes : this.getDefaultNodes(courseId);
      
      return {
        path_id: `${userId}_${courseId}`,
        title: progressResponse.title || 'Learning Path',
        description: progressResponse.description || 'Your personalized learning journey',
        nodes: finalNodes,
        current_node_id: finalNodes.find(node => node.status === 'current')?.id || finalNodes[0]?.id || 'node_1',
        progress_percentage: progressResponse.progress || 0,
        estimated_total_duration: finalNodes.reduce((total, node) => total + node.duration, 0) || 120
      };
    } catch (error) {
      console.error('Error in getLearningPath:', error);
      // Return a fallback learning path if everything fails
      return this.getFallbackLearningPath(userId, courseId);
    }
  }

  // System Information
  async getSystemStatus(): Promise<Record<string, any>> {
    try {
      const response = await api.get(`${this.baseUrl}/system-status`);
      return response.data;
    } catch (error: any) {
      console.error('Error getting system status:', error);
      return {
        status: 'unknown',
        message: 'Unable to connect to backend'
      };
    }
  }

  async getAvailableSubjects(): Promise<{ subjects: string[] }> {
    try {
      const response = await api.get(`${this.baseUrl}/available-subjects`);
      return response.data;
    } catch (error: any) {
      console.error('Error getting available subjects:', error);
      return {
        subjects: [
          'Mathematics',
          'Science',
          'Programming',
          'History',
          'Literature'
        ]
      };
    }
  }

  async getLearningStyles(): Promise<{ styles: LearningStyle[] }> {
    try {
      const response = await api.get(`${this.baseUrl}/learning-styles`);
      return response.data;
    } catch (error: any) {
      console.error('Error getting learning styles:', error);
      return {
        styles: [
          { value: 'visual', label: 'Visual', description: 'Learn through diagrams and visual aids' },
          { value: 'auditory', label: 'Auditory', description: 'Learn through listening and verbal explanations' },
          { value: 'kinesthetic', label: 'Kinesthetic', description: 'Learn through hands-on activities' }
        ]
      };
    }
  }

  async getDifficultyLevels(): Promise<{ levels: DifficultyLevel[] }> {
    try {
      const response = await api.get(`${this.baseUrl}/difficulty-levels`);
      return response.data;
    } catch (error: any) {
      console.error('Error getting difficulty levels:', error);
      return {
        levels: [
          { value: 'beginner', label: 'Beginner', description: 'New to the subject' },
          { value: 'intermediate', label: 'Intermediate', description: 'Some experience' },
          { value: 'advanced', label: 'Advanced', description: 'Experienced learner' }
        ]
      };
    }
  }

  // Private helper methods
  private transformToLearningPath(progressData: any): LearningPathNode[] {
    console.log('Transforming progress data:', progressData);
    
    if (!progressData) {
      console.log('No progress data available, returning empty array');
      return [];
    }

    // If we have curriculum data from the backend, transform it
    if (progressData.curriculum && Array.isArray(progressData.curriculum)) {
      return progressData.curriculum.map((lesson: any, index: number) => ({
        id: `lesson_${lesson.id || index}`,
        type: 'lesson' as const,
        title: lesson.title || `Lesson ${index + 1}`,
        description: lesson.description || `Learn about ${lesson.title || 'the topic'}`,
        status: index === 0 ? 'current' as const : 'locked' as const,
        duration: lesson.duration || 30,
        difficulty: lesson.difficulty || 'medium',
        prerequisites: lesson.prerequisites || [],
        metadata: {
          learning_objectives: lesson.learning_objectives || [],
          content: lesson.content || ''
        }
      }));
    }

    // If we have a different structure, try to adapt
    if (progressData.lessons && Array.isArray(progressData.lessons)) {
      return progressData.lessons.map((lesson: any, index: number) => ({
        id: `lesson_${lesson.id || index}`,
        type: 'lesson' as const,
        title: lesson.title || `Lesson ${index + 1}`,
        description: lesson.description || `Learn about ${lesson.title || 'the topic'}`,
        status: index === 0 ? 'current' as const : 'locked' as const,
        duration: lesson.duration || 30,
        difficulty: lesson.difficulty || 'medium',
        prerequisites: lesson.prerequisites || [],
        metadata: {
          learning_objectives: lesson.learning_objectives || [],
          content: lesson.content || ''
        }
      }));
    }

    console.log('No recognizable curriculum structure, returning empty array');
    return [];
  }

  private getDefaultNodes(courseId: string): LearningPathNode[] {
    console.log('Creating default nodes for course:', courseId);
    return [
      {
        id: 'node_1',
        type: 'lesson',
        title: 'Introduction',
        description: 'Get started with the course',
        status: 'current',
        duration: 30,
        difficulty: 'beginner',
        prerequisites: []
      },
      {
        id: 'node_2', 
        type: 'lesson',
        title: 'Core Concepts',
        description: 'Learn the fundamental concepts',
        status: 'locked',
        duration: 45,
        difficulty: 'beginner',
        prerequisites: ['node_1']
      },
      {
        id: 'node_3',
        type: 'assessment',
        title: 'Knowledge Check',
        description: 'Test your understanding',
        status: 'locked',
        duration: 20,
        difficulty: 'beginner',
        prerequisites: ['node_2']
      }
    ];
  }

  private getFallbackLearningPath(userId: string, courseId: string): LearningPathData {
    console.log('Creating fallback learning path for:', { userId, courseId });
    const nodes = this.getDefaultNodes(courseId);
    return {
      path_id: `${userId}_${courseId}_fallback`,
      title: 'Learning Path',
      description: 'Your personalized learning journey',
      nodes: nodes,
      current_node_id: nodes[0].id,
      progress_percentage: 0,
      estimated_total_duration: nodes.reduce((total, node) => total + node.duration, 0)
    };
  }

  private getMockAssessment(lessonId: string): AssessmentResponse {
    console.log('Creating mock assessment for lesson:', lessonId);
    return {
      assessment_id: `mock_assessment_${lessonId}_${Date.now()}`,
      questions: [
        {
          id: 'q1',
          question: 'What is the main concept covered in this lesson?',
          type: 'multiple_choice',
          options: ['Concept A', 'Concept B', 'Concept C', 'Concept D'],
          correct_answer: 'Concept A',
          explanation: 'This was the primary focus of the lesson material.'
        },
        {
          id: 'q2',
          question: 'True or False: The principles discussed apply to all scenarios.',
          type: 'true_false',
          correct_answer: 'false',
          explanation: 'There are exceptions to these principles.'
        },
        {
          id: 'q3',
          question: 'Explain how you would apply this knowledge in a real-world situation.',
          type: 'short_answer',
          correct_answer: 'Open-ended response demonstrating understanding',
          explanation: 'This tests your ability to apply theoretical knowledge practically.'
        }
      ],
      time_limit: 30,
      passing_score: 0.7
    };
  }

  private getMockEvaluation(request: EvaluateAssessmentRequest): EvaluateAssessmentResponse {
    console.log('Creating mock evaluation for assessment:', request.assessment_id);
    
    // Simple scoring logic for mock
    const totalQuestions = Object.keys(request.user_answers).length;
    const correctAnswers = Math.floor(totalQuestions * 0.8); // Mock 80% score
    const score = correctAnswers / totalQuestions;
    const passed = score >= 0.7;

    return {
      score,
      passed,
      gaps: passed ? [] : [
        {
          concept: 'Core Principles',
          severity: 'medium',
          description: 'Need better understanding of fundamental concepts',
          remedial_suggestions: [
            'Review the introductory materials',
            'Practice with additional examples',
            'Focus on the key definitions'
          ]
        }
      ],
      remedial_content: {
        title: 'Review Materials',
        content: 'Please review the core concepts section and practice with the provided examples.',
        resources: [
          'Lesson slides',
          'Practice exercises',
          'Additional reading materials'
        ]
      },
      next_steps: passed 
        ? ['Proceed to next lesson', 'Explore advanced topics'] 
        : ['Review the materials', 'Retry the assessment']
    };
  }
}

// Export singleton instance
export const agentService = new AgentService();
export default agentService;