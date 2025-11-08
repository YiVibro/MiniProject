import { useState, useEffect, useCallback } from 'react';
import { useToast } from '@/components/ui/use-toast';
import { agentService, type LearningPathData, type LearningPathNode, type AssessmentResponse, type EvaluateAssessmentResponse } from '@/lib/agentService';
import { useAuth } from '@/store/AuthContext';

export interface LearningPathState {
  data: LearningPathData | null;
  currentLesson: LearningPathNode | null;
  assessment: AssessmentResponse | null;
  assessmentResults: EvaluateAssessmentResponse | null;
  isLoading: boolean;
  isAssessing: boolean;
  progress: number;
}

export interface LearningPathActions {
  loadLearningPath: (courseId: string) => Promise<void>;
  startLesson: (nodeId: string) => Promise<void>;
  completeLesson: (nodeId: string) => Promise<void>;
  startAssessment: (lessonId: string) => Promise<void>;
  submitAssessment: (answers: Record<string, any>) => Promise<void>;
  unlockNextNode: () => void;
  updateProgress: (progress: number) => void;
}

export const useLearningPath = (): LearningPathState & LearningPathActions => {
  const [data, setData] = useState<LearningPathData | null>(null);
  const [currentLesson, setCurrentLesson] = useState<LearningPathNode | null>(null);
  const [assessment, setAssessment] = useState<AssessmentResponse | null>(null);
  const [assessmentResults, setAssessmentResults] = useState<EvaluateAssessmentResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isAssessing, setIsAssessing] = useState(false);
  const [progress, setProgress] = useState(0);

  const { user } = useAuth();
  const { toast } = useToast();

  const loadLearningPath = useCallback(async (courseId: string) => {
    console.log('loadLearningPath called with courseId:', courseId);
    console.log('Current user:', user);

    if (!user || !user.id) {
      console.error('User not available in loadLearningPath');
      toast({
        title: 'Authentication required',
        description: 'Please log in to load your learning path',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsLoading(true);
      console.log('Calling agentService.getLearningPath with:', user.id, courseId);
      
      const pathData = await agentService.getLearningPath(user.id, courseId);
      console.log('Received pathData:', pathData);
      
      setData(pathData);
      
      // Set current lesson
      const current = pathData.nodes.find(node => node.id === pathData.current_node_id);
      setCurrentLesson(current || null);
      setProgress(pathData.progress_percentage);
      
    } catch (error: any) {
      console.error('Error loading learning path:', error);
      console.error('Error details:', {
        message: error.message,
        stack: error.stack,
        user: user,
        courseId: courseId
      });
      
      toast({
        title: 'Failed to load learning path',
        description: error.message || 'Please try again later',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [user, toast]);

  const startLesson = useCallback(async (nodeId: string) => {
    if (!user || !data) return;

    try {
      console.log('Starting lesson:', nodeId);
      // Start learning session with backend
      const sessionResponse = await agentService.startLearningSession({
        user_id: user.id,
        lesson_id: nodeId,
        session_preferences: {
          node_type: data.nodes.find(n => n.id === nodeId)?.type,
          difficulty: data.nodes.find(n => n.id === nodeId)?.difficulty
        }
      });

      // Update UI state
      setData(prev => prev ? {
        ...prev,
        current_node_id: nodeId
      } : null);

      setCurrentLesson(data.nodes.find(n => n.id === nodeId) || null);

      toast({
        title: 'Lesson started!',
        description: 'Your learning session has begun',
      });

    } catch (error: any) {
      console.error('Error starting lesson:', error);
      toast({
        title: 'Failed to start lesson',
        description: error.message || 'Please try again',
        variant: 'destructive',
      });
    }
  }, [user, data, toast]);

  const completeLesson = useCallback(async (nodeId: string) => {
    if (!user || !data) return;

    try {
      console.log('Completing lesson:', nodeId);
      // Mark lesson as completed in backend
      await agentService.trackProgress({
        user_id: user.id,
        activity: 'lesson_completed',
        data: {
          node_id: nodeId,
          completion_time: new Date().toISOString()
        }
      });

      // Update local state
      setData(prev => {
        if (!prev) return null;
        
        const updatedNodes = prev.nodes.map(node => 
          node.id === nodeId 
            ? { ...node, status: 'completed' as const }
            : node
        );

        // Calculate new progress
        const completedCount = updatedNodes.filter(n => n.status === 'completed').length;
        const newProgress = (completedCount / updatedNodes.length) * 100;

        setProgress(newProgress);

        return {
          ...prev,
          nodes: updatedNodes,
          progress_percentage: newProgress
        };
      });

      toast({
        title: 'Lesson completed! 🎉',
        description: 'Great job! Ready for practice?',
      });

    } catch (error: any) {
      console.error('Error completing lesson:', error);
      toast({
        title: 'Error completing lesson',
        description: error.message || 'Progress may not be saved',
        variant: 'destructive',
      });
    }
  }, [user, data, toast]);

  const startAssessment = useCallback(async (lessonId: string) => {
    if (!user) return;

    try {
      console.log('Starting assessment for lesson:', lessonId);
      setIsAssessing(true);
      const assessmentData = await agentService.createAssessment({
        lesson_id: lessonId,
        num_questions: 5,
        difficulty: 'medium'
      });
      
      setAssessment(assessmentData);
      
      toast({
        title: 'Assessment started',
        description: `Complete ${assessmentData.questions.length} questions`,
      });

    } catch (error: any) {
      console.error('Error starting assessment:', error);
      toast({
        title: 'Failed to start assessment',
        description: error.message || 'Please try again',
        variant: 'destructive',
      });
    } finally {
      setIsAssessing(false);
    }
  }, [user, toast]);

  const submitAssessment = useCallback(async (answers: Record<string, any>) => {
    if (!user || !assessment) return;

    try {
      console.log('Submitting assessment with answers:', answers);
      setIsAssessing(true);
      const results = await agentService.evaluateAssessment({
        assessment_id: assessment.assessment_id,
        user_answers: answers,
        user_id: user.id
      });

      setAssessmentResults(results);

      if (results.passed) {
        toast({
          title: 'Assessment passed! 🎉',
          description: `Score: ${(results.score * 100).toFixed(1)}%`,
        });
      } else {
        toast({
          title: 'Assessment results',
          description: `Score: ${(results.score * 100).toFixed(1)}% - Review recommended`,
          variant: 'destructive',
        });
      }

    } catch (error: any) {
      console.error('Error submitting assessment:', error);
      toast({
        title: 'Error submitting assessment',
        description: error.message || 'Please try again',
        variant: 'destructive',
      });
    } finally {
      setIsAssessing(false);
    }
  }, [user, assessment, toast]);

  const unlockNextNode = useCallback(() => {
    console.log('Unlocking next node');
    setData(prev => {
      if (!prev) return null;

      const currentIndex = prev.nodes.findIndex(node => node.id === prev.current_node_id);
      if (currentIndex === -1 || currentIndex >= prev.nodes.length - 1) return prev;

      const nextNodeId = prev.nodes[currentIndex + 1].id;
      const updatedNodes = prev.nodes.map((node, index) => 
        index === currentIndex + 1 
          ? { ...node, status: 'current' as const }
          : node
      );

      return {
        ...prev,
        nodes: updatedNodes,
        current_node_id: nextNodeId
      };
    });
  }, []);

  const updateProgress = useCallback((newProgress: number) => {
    console.log('Updating progress to:', newProgress);
    setProgress(newProgress);
  }, []);

  return {
    // State
    data,
    currentLesson,
    assessment,
    assessmentResults,
    isLoading,
    isAssessing,
    progress,

    // Actions
    loadLearningPath,
    startLesson,
    completeLesson,
    startAssessment,
    submitAssessment,
    unlockNextNode,
    updateProgress
  };
};