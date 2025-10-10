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

export class AgentService {
  private baseUrl = '/api/agents';

  // Learning Plan Management
  async createLearningPlan(request: CreateLearningPlanRequest): Promise<LearningPlanResponse> {
    const response = await api.post(`${this.baseUrl}/create-learning-plan`, request);
    return response.data;
  }

  async getLearningPlanStatus(userId: string): Promise<Record<string, any>> {
    const response = await api.get(`${this.baseUrl}/learning-plan-status/${userId}`);
    return response.data;
  }

  // Course Creation
  async createCourse(request: CreateCourseRequest): Promise<CourseResponse> {
    const response = await api.post(`${this.baseUrl}/create-course`, request);
    return response.data;
  }

  // Progress Tracking
  async trackProgress(request: ProgressTrackingRequest): Promise<ProgressResponse> {
    const response = await api.post(`${this.baseUrl}/track-progress`, request);
    return response.data;
  }

  // Learning Sessions
  async startLearningSession(request: LearningSessionRequest): Promise<LearningSessionResponse> {
    const response = await api.post(`${this.baseUrl}/start-learning-session`, request);
    return response.data;
  }

  async processUserInteraction(
    sessionId: string,
    interactionType: string,
    interactionData: Record<string, any>
  ): Promise<Record<string, any>> {
    const response = await api.post(`${this.baseUrl}/process-interaction`, {
      session_id: sessionId,
      interaction_type: interactionType,
      interaction_data: interactionData
    });
    return response.data;
  }

  async endLearningSession(sessionId: string): Promise<Record<string, any>> {
    const response = await api.post(`${this.baseUrl}/end-learning-session/${sessionId}`);
    return response.data;
  }

  // System Information
  async getSystemStatus(): Promise<Record<string, any>> {
    const response = await api.get(`${this.baseUrl}/system-status`);
    return response.data;
  }

  async getAvailableSubjects(): Promise<{ subjects: string[] }> {
    const response = await api.get(`${this.baseUrl}/available-subjects`);
    return response.data;
  }

  async getLearningStyles(): Promise<{ styles: LearningStyle[] }> {
    const response = await api.get(`${this.baseUrl}/learning-styles`);
    return response.data;
  }

  async getDifficultyLevels(): Promise<{ levels: DifficultyLevel[] }> {
    const response = await api.get(`${this.baseUrl}/difficulty-levels`);
    return response.data;
  }
}

// Export singleton instance
export const agentService = new AgentService();
export default agentService;


