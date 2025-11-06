import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { useAuth } from '../store/AuthContext';
import { agentService } from '../lib/agentService';
import { useToast } from './ui/use-toast';
import { Sparkles, BookOpen, Target, Clock, CheckCircle2, PlayCircle, TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { CourseLearnView } from './CourseLearnView';

interface LearningPlan {
  path_id: string;
  requirements: {
    subject: string;
    current_level: string;
    timeline: string;
    goals: string[];
    time_per_day: string;
  };
  curriculum: Array<{
    id: string;
    title: string;
    difficulty: string;
    completed?: boolean;
    progress?: number;
  }>;
  timeline: string;
  goals: string[];
}

interface PlanStatus {
  plan_id: string;
  current_week: number;
  progress: {
    lessons_completed: number;
    average_score: number;
    recommendations: string[];
  };
  curriculum?: Array<{
    id: string;
    title: string;
    difficulty: string;
    completed?: boolean;
    progress?: number;
  }>;
}

const DynamicCourseGenerator = () => {
  const [userRequest, setUserRequest] = useState('');
  const [learningPlan, setLearningPlan] = useState<LearningPlan | null>(null);
  const [planStatus, setPlanStatus] = useState<PlanStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusLoading, setStatusLoading] = useState(false);
  const [activeSession, setActiveSession] = useState<{
    sessionId: string;
    lessonId: string;
    lessonTitle: string;
  } | null>(null);
  const { user } = useAuth();
  const { toast } = useToast();

  // Fetch existing plan status on mount
  useEffect(() => {
    if (user) {
      fetchPlanStatus();
    }
  }, [user]);

  const fetchPlanStatus = async () => {
    if (!user) return;
    
    try {
      setStatusLoading(true);
      const status = await agentService.getLearningPlanStatus(user.id);
      if (status && !status.error) {
        setPlanStatus(status as PlanStatus);
      }
    } catch (error) {
      console.log('No existing plan found');
    } finally {
      setStatusLoading(false);
    }
  };

  const handleGeneratePlan = async () => {
    if (!userRequest.trim()) {
      toast({
        title: "Input Required",
        description: "Please describe what you want to learn.",
        variant: "destructive",
      });
      return;
    }

    if (!user) {
      toast({
        title: "Authentication Required",
        description: "Please log in to create a learning plan.",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const plan = await agentService.createLearningPlan({
        user_id: user.id,
        user_request: userRequest,
        preferences: {}
      });

      setLearningPlan(plan as any as LearningPlan);
      
      toast({
        title: "Learning Plan Created! 🎉",
        description: `Your personalized ${plan.requirements.subject} course is ready!`,
      });

      // Fetch updated status
      await fetchPlanStatus();
    } catch (error: any) {
      console.error('Error generating plan:', error);
      toast({
        title: "Generation Failed",
        description: error.message || "Failed to create learning plan. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStartLesson = async (lessonId: string, lessonTitle: string) => {
    if (!user) {
      toast({
        title: "Authentication Required",
        description: "Please log in to start learning.",
        variant: "destructive",
      });
      return;
    }

    try {
      const sessionResponse = await agentService.startLearningSession({
        user_id: user.id,
        lesson_id: lessonId,
        session_preferences: {
          course_name: learningPlan?.requirements.subject || "Course",
          difficulty: learningPlan?.requirements.current_level || "medium"
        }
      });

      setActiveSession({
        sessionId: sessionResponse.session_id,
        lessonId: lessonId,
        lessonTitle: lessonTitle
      });

      toast({
        title: "Session Started! 🚀",
        description: `Starting ${lessonTitle}...`,
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to start session.",
        variant: "destructive",
      });
    }
  };

  const exampleRequests = [
    "I want to learn Python for 3 months with weekly tests",
    "Teach me Machine Learning for 6 months with projects",
    "I need to master JavaScript in 8 weeks for a job interview",
    "Help me learn Web Development in 4 months"
  ];

  // Show CourseLearnView if there's an active session
  if (activeSession) {
    return (
      <CourseLearnView
        sessionId={activeSession.sessionId}
        lessonId={activeSession.lessonId}
        lessonTitle={activeSession.lessonTitle}
        courseSubject={learningPlan?.requirements.subject || "Course"}
        onBack={() => setActiveSession(null)}
      />
    );
  }

  return (
    <Card className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/20 dark:to-blue-950/20 border-purple-200 dark:border-purple-800">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-500" />
          AI Course Generator
        </CardTitle>
        <CardDescription>
          Describe what you want to learn, and AI will create a personalized course
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Input Section */}
        <div className="space-y-3">
          <Textarea
            placeholder="Example: I want to learn Python for 3 months with weekly tests..."
            value={userRequest}
            onChange={(e) => setUserRequest(e.target.value)}
            className="min-h-[100px] bg-white dark:bg-gray-900"
            disabled={loading}
          />
          
          {/* Example Prompts */}
          <div className="flex flex-wrap gap-2">
            {exampleRequests.map((example, idx) => (
              <Button
                key={idx}
                variant="outline"
                size="sm"
                className="text-xs"
                onClick={() => setUserRequest(example)}
                disabled={loading}
              >
                {example.substring(0, 30)}...
              </Button>
            ))}
          </div>

          <Button 
            onClick={handleGeneratePlan} 
            disabled={loading || !userRequest.trim()}
            className="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
          >
            {loading ? (
              <>
                <Clock className="w-4 h-4 mr-2 animate-spin" />
                Generating Your Plan...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Learning Plan
              </>
            )}
          </Button>
        </div>

        {/* Generated Plan Display */}
        <AnimatePresence>
          {learningPlan && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4 mt-6"
            >
              {/* Plan Overview */}
              <div className="p-4 bg-white dark:bg-gray-900 rounded-lg border border-purple-200 dark:border-purple-800">
                <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                  <Target className="w-5 h-5 text-purple-500" />
                  Your Learning Plan
                </h3>
                
                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Subject</p>
                    <Badge variant="secondary" className="mt-1">
                      {learningPlan.requirements.subject}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Level</p>
                    <Badge variant="secondary" className="mt-1">
                      {learningPlan.requirements.current_level}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Timeline</p>
                    <p className="font-medium">{learningPlan.timeline}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Daily Time</p>
                    <p className="font-medium">{learningPlan.requirements.time_per_day}</p>
                  </div>
                </div>

                {/* Goals */}
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Learning Goals</p>
                  <div className="flex flex-wrap gap-2">
                    {learningPlan.goals.map((goal, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs">
                        {goal}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>

              {/* Curriculum */}
              <div className="p-4 bg-white dark:bg-gray-900 rounded-lg border border-purple-200 dark:border-purple-800">
                <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-blue-500" />
                  Curriculum ({learningPlan.curriculum.length} Lessons)
                </h3>
                
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {learningPlan.curriculum.map((lesson, idx) => (
                    <motion.div
                      key={lesson.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-blue-400 flex items-center justify-center text-white font-semibold text-sm">
                          {idx + 1}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-sm">{lesson.title}</p>
                          <Badge variant="outline" className="text-xs mt-1">
                            {lesson.difficulty}
                          </Badge>
                        </div>
                      </div>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleStartLesson(lesson.id, lesson.title)}
                        className="text-purple-600 hover:text-purple-700 hover:bg-purple-50"
                      >
                        <PlayCircle className="w-4 h-4 mr-1" />
                        Start
                      </Button>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Existing Plan Status */}
        <AnimatePresence>
          {planStatus && !learningPlan && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 bg-white dark:bg-gray-900 rounded-lg border border-green-200 dark:border-green-800"
            >
              <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-500" />
                Your Progress
              </h3>
              
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Lessons Completed</span>
                    <span className="font-medium">
                      {planStatus.progress.lessons_completed}
                    </span>
                  </div>
                  <Progress 
                    value={planStatus.progress.lessons_completed * 10} 
                    className="h-2"
                  />
                </div>

                {planStatus.progress.average_score > 0 && (
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Average Score</span>
                      <span className="font-medium">
                        {planStatus.progress.average_score.toFixed(1)}%
                      </span>
                    </div>
                    <Progress 
                      value={planStatus.progress.average_score} 
                      className="h-2"
                    />
                  </div>
                )}

                {planStatus.progress.recommendations && 
                 planStatus.progress.recommendations.length > 0 && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Recommendations</p>
                    <div className="space-y-1">
                      {planStatus.progress.recommendations.map((rec, idx) => (
                        <div key={idx} className="flex items-start gap-2 text-sm">
                          <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                          <span>{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
};

export default DynamicCourseGenerator;
