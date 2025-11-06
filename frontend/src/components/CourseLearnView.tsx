import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { useAuth } from "../store/AuthContext";
import { useToast } from "@/components/ui/use-toast";
import { MessageBubble } from "./MessageBubble";
import { motion } from "framer-motion";
import { agentService } from "../lib/agentService";
import { 
  ArrowLeft, 
  BookOpen, 
  CheckCircle2,
  Lock,
  Brain,
  PlayCircle,
  PenTool,
  Trophy,
  Send
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

type QuickAction = {
  label: string;
  icon: LucideIcon;
  action: string;
  prompt: string;
};

interface CourseLearnViewProps {
  sessionId: string;
  lessonId: string;
  lessonTitle: string;
  courseSubject: string;
  onBack: () => void;
}

interface LessonContent {
  id: string;
  title: string;
  content: string;
  examples: string[];
  practice: {
    questions: string[];
    solutions: string[];
  };
  objectives: string[];
  prerequisites: string[];
}

interface LessonStep {
  id: string;
  title: string;
  type: 'concept' | 'practice' | 'assessment';
  status: 'locked' | 'available' | 'in-progress' | 'completed';
  progress: number;
  score?: number;
  content?: LessonContent;
  requirements?: string[];
}

interface AssessmentResult {
  score: number;
  feedback: string[];
  nextSteps: string[];
  mastered: string[];
  gaps: string[];
  recommendations: string[];
  remedialContent?: string;
}

interface PracticeResult {
  correct: boolean;
  feedback: string;
  hints: string[];
  nextQuestion?: string;
  masteryLevel: number;
}

interface LearningProgress {
  conceptsMastered: string[];
  currentLevel: string;
  learningCurve: {
    date: string;
    score: number;
  }[];
  recommendedTopics: string[];
  timeSpent: number;
}

interface Message {
  sender: 'user' | 'ai';
  text: string;
}

const WELCOME_MESSAGE = "Welcome to your interactive learning session! I'm your AI tutor. Let me help you master these concepts step by step.";

const QUICK_ACTIONS: QuickAction[] = [
  {
    label: "Explain Concept",
    icon: Brain,
    action: "explain_concept",
    prompt: "Please explain this concept in detail"
  },
  {
    label: "Show Example",
    icon: PlayCircle,
    action: "show_example",
    prompt: "Can you show me a practical example?"
  },
  {
    label: "Practice",
    icon: PenTool,
    action: "start_practice",
    prompt: "I want to practice this concept"
  },
  {
    label: "Test Knowledge",
    icon: Trophy,
    action: "test_knowledge",
    prompt: "Test my understanding of this concept"
  }
];

export const CourseLearnView = ({ 
  sessionId, 
  lessonId, 
  lessonTitle, 
  courseSubject,
  onBack 
}: CourseLearnViewProps): JSX.Element => {
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [loading, setLoading] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [lessonSteps, setLessonSteps] = useState<LessonStep[]>([]);
  const [currentStep, setCurrentStep] = useState<LessonStep | null>(null);
  const [practiceAnswer, setPracticeAnswer] = useState('');
  const [practiceResult, setPracticeResult] = useState<PracticeResult | null>(null);
  const [assessmentResult, setAssessmentResult] = useState<AssessmentResult | null>(null);
  const [learningProgress, setLearningProgress] = useState<LearningProgress>({
    conceptsMastered: [],
    currentLevel: 'beginner',
    learningCurve: [],
    recommendedTopics: [],
    timeSpent: 0
  });

  // Initialize lesson and learning path
  useEffect(() => {
    if (!sessionId || !lessonId || !user?.id) return;

    const initializeSession = async () => {
      try {
        setLoading(true);
        
        // Initialize learning path
        const learningPlan = await agentService.processUserInteraction(
          sessionId,
          "initialize_learning_path",
          {
            user_id: user.id,
            lesson_id: lessonId
          }
        );

        setLessonSteps(learningPlan.steps.map((step: any, index: number) => ({
          ...step,
          status: index === 0 ? 'available' : 'locked'
        })));

        // Set first step as current
        if (learningPlan.steps.length > 0) {
          setCurrentStep(learningPlan.steps[0]);
        }

        // Set initial progress
        setLearningProgress(learningPlan.initial_progress);

        toast({
          title: "Ready to learn! 🚀",
          description: "Your personalized learning path has been created.",
        });

      } catch (error: any) {
        console.error("Error initializing session:", error);
        toast({
          title: "Error",
          description: "Failed to initialize learning session.",
          variant: "destructive"
        });
      } finally {
        setLoading(false);
      }
    };

    initializeSession();
  }, [sessionId, lessonId, user?.id]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    // Add user message
    setMessages(prev => [...prev, { sender: 'user', text: input }]);
    const userMessage = input;
    setInput('');
    setLoading(true);

    try {
      const response = await agentService.processUserInteraction(
        sessionId,
        "chat_message",
        { 
          message: userMessage,
          user_id: user?.id,
          lesson_id: lessonId,
          current_step: currentStep?.id,
          context: {
            subject: courseSubject,
            step_type: currentStep?.type,
            progress: learningProgress
          }
        }
      );

      setMessages(prev => [...prev, { 
        sender: 'ai', 
        text: response.response || response.message || "I'm here to help you learn!" 
      }]);

    } catch (error: any) {
      console.error("Error sending message:", error);
      setMessages(prev => [...prev, { 
        sender: 'ai', 
        text: "Sorry, I encountered an error. Please try again." 
      }]);
      toast({
        title: "Error",
        description: "Failed to process your message.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = async (action: string, prompt: string) => {
    setMessages(prev => [...prev, { sender: 'user', text: prompt }]);
    setLoading(true);

    try {
      const response = await agentService.processUserInteraction(
        sessionId,
        action,
        { 
          user_id: user?.id,
          lesson_id: lessonId,
          current_step: currentStep?.id,
          action_type: action,
          context: {
            subject: courseSubject,
            step_type: currentStep?.type,
            progress: learningProgress
          }
        }
      );

      setMessages(prev => [...prev, { 
        sender: 'ai', 
        text: response.response || response.message || "Here's what I found!" 
      }]);

    } catch (error: any) {
      console.error("Error with quick action:", error);
      setMessages(prev => [...prev, { 
        sender: 'ai', 
        text: "Sorry, I couldn't process that request." 
      }]);
      toast({
        title: "Error",
        description: "Failed to process quick action.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStepComplete = async (step: LessonStep) => {
    setLoading(true);
    try {
      if (step.type === 'concept') {
        // Process concept completion with dynamic_lesson_generator
        const conceptResponse = await agentService.processUserInteraction(
          sessionId,
          "complete_concept",
          {
            user_id: user?.id,
            lesson_id: lessonId,
            concept_id: step.content?.id
          }
        );

        // Update progress
        await updateStepStatus(step.id, 'completed');
        const nextStep = lessonSteps.find(s => s.status === 'locked');
        if (nextStep) {
          await updateStepStatus(nextStep.id, 'available');
        }

      } else if (step.type === 'practice') {
        // Process practice with enhanced_tutoring_system
        const practiceResponse = await agentService.processUserInteraction(
          sessionId,
          "evaluate_practice",
          {
            user_id: user?.id,
            lesson_id: lessonId,
            step_id: step.id,
            answer: practiceAnswer
          }
        );

        // Type assertion to handle API response
        const typedPracticeResponse: PracticeResult = {
          correct: practiceResponse.correct,
          feedback: practiceResponse.feedback,
          hints: practiceResponse.hints || [],
          nextQuestion: practiceResponse.nextQuestion,
          masteryLevel: practiceResponse.masteryLevel
        };
        setPracticeResult(typedPracticeResponse);

        if (typedPracticeResponse.masteryLevel >= 0.8) {
          await updateStepStatus(step.id, 'completed');
          const nextStep = lessonSteps.find(s => s.status === 'locked');
          if (nextStep) {
            await updateStepStatus(nextStep.id, 'available');
          }
        }

      } else if (step.type === 'assessment') {
        // Process assessment with assessment_system
        const assessmentResponse = await agentService.processUserInteraction(
          sessionId,
          "complete_assessment",
          {
            user_id: user?.id,
            lesson_id: lessonId,
            step_id: step.id
          }
        );

        // Type assertion to handle API response
        const typedAssessmentResponse: AssessmentResult = {
          score: assessmentResponse.score,
          feedback: assessmentResponse.feedback || [],
          nextSteps: assessmentResponse.nextSteps || [],
          mastered: assessmentResponse.mastered || [],
          gaps: assessmentResponse.gaps || [],
          recommendations: assessmentResponse.recommendations || [],
          remedialContent: assessmentResponse.remedialContent
        };
        setAssessmentResult(typedAssessmentResponse);

        // Analyze knowledge gaps
        const gapAnalysis = await agentService.processUserInteraction(
          sessionId,
          "analyze_gaps",
          {
            user_id: user?.id,
            lesson_id: lessonId,
            assessment_result: typedAssessmentResponse
          }
        );

        // Update learning progress
        const progressUpdate = await agentService.processUserInteraction(
          sessionId,
          "update_learning_curve",
          {
            user_id: user?.id,
            lesson_id: lessonId,
            assessment_score: typedAssessmentResponse.score
          }
        );

        setLearningProgress(progressUpdate.progress);

        if (typedAssessmentResponse.score >= 70) {
          await updateStepStatus(step.id, 'completed');
          toast({
            title: "Assessment Completed! 🎉",
            description: `You scored ${typedAssessmentResponse.score}%! Great job!`,
          });
        } else {
          toast({
            title: "Keep Practicing",
            description: "Review the concepts and try again when ready.",
          });
        }
      }
    } catch (error: any) {
      console.error("Error completing step:", error);
      toast({
        title: "Error",
        description: "Failed to process step completion.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const updateStepStatus = async (stepId: string, status: LessonStep['status']) => {
    setLessonSteps(steps => 
      steps.map(step => 
        step.id === stepId ? { ...step, status } : step
      )
    );
  };

  const StepIcon = ({ type, status }: { type: LessonStep['type'], status: LessonStep['status'] }) => {
    const icons: Record<LessonStep['type'], LucideIcon> = {
      concept: Brain,
      practice: PenTool,
      assessment: Trophy
    };
    const Icon = icons[type];

    if (status === 'locked') {
      return <Lock className="w-5 h-5 text-muted-foreground" />;
    }
    return <Icon className={`w-5 h-5 ${status === 'completed' ? 'text-green-500' : 'text-blue-500'}`} />;
  };

  const completedSteps = lessonSteps.filter(s => s.status === 'completed').length;
  const totalSteps = lessonSteps.length;
  const progressPercentage = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <div className="border-b bg-card p-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={onBack} size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-2xl font-bold">{lessonTitle}</h1>
              <p className="text-sm text-muted-foreground flex items-center gap-2 mt-1">
                <BookOpen className="w-4 h-4" />
                {courseSubject}
              </p>
            </div>
          </div>
          <Badge variant="secondary" className="text-sm">
            Learning Session Active
          </Badge>
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex max-w-7xl mx-auto w-full">
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Quick Actions */}
          <div className="p-4 border-b bg-card">
            <div className="flex gap-2 flex-wrap">
              {QUICK_ACTIONS.map((action, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  size="sm"
                  onClick={() => handleQuickAction(action.action, action.prompt)}
                  disabled={loading}
                  className="gap-2"
                >
                  <action.icon className="w-4 h-4" />
                  {action.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <MessageBubble sender="ai" text={WELCOME_MESSAGE} />
              </motion.div>
            )}
            
            {messages.map((message, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <MessageBubble sender={message.sender} text={message.text} />
              </motion.div>
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                <span className="ml-2">AI is thinking...</span>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="p-4 border-t bg-card">
            <div className="flex gap-2">
              <Input
                placeholder="Ask a question or request help..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
                disabled={loading}
                className="flex-1"
              />
              <Button onClick={sendMessage} disabled={loading || !input.trim()}>
                <Send className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Press Enter to send • Shift + Enter for new line
            </p>
          </div>
        </div>

        {/* Sidebar - Progress & Tips */}
        <div className="w-80 border-l bg-card p-4 space-y-4 overflow-y-auto">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Lesson Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Completion</span>
                  <span className="font-medium">{progressPercentage}%</span>
                </div>
                <Progress 
                  value={progressPercentage} 
                  className="h-2" 
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Learning Steps</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {lessonSteps.map((step, idx) => (
                <div 
                  key={step.id}
                  className={`flex items-center gap-3 p-2 rounded-lg border ${
                    step.status === 'available' ? 'bg-blue-50 border-blue-200 dark:bg-blue-950/20 dark:border-blue-800' :
                    step.status === 'completed' ? 'bg-green-50 border-green-200 dark:bg-green-950/20 dark:border-green-800' :
                    'bg-muted/20 border-muted'
                  }`}
                >
                  <StepIcon type={step.type} status={step.status} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{step.title}</p>
                    <p className="text-xs text-muted-foreground capitalize">{step.type}</p>
                  </div>
                  {step.status === 'available' && (
                    <Button 
                      size="sm" 
                      variant="ghost"
                      onClick={() => handleStepComplete(step)}
                      disabled={loading}
                    >
                      Start
                    </Button>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Learning Tips</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-start gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Ask questions whenever you're confused</span>
              </div>
              <div className="flex items-start gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Request examples to understand better</span>
              </div>
              <div className="flex items-start gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Try practice problems to reinforce learning</span>
              </div>
              <div className="flex items-start gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Take notes of important concepts</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/20 dark:to-blue-950/20">
            <CardHeader>
              <CardTitle className="text-sm">Session Info</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div>
                <p className="text-muted-foreground text-xs">Session ID</p>
                <p className="font-mono text-xs">{sessionId.substring(0, 8)}...</p>
              </div>
              <div>
                <p className="text-muted-foreground text-xs">Lesson</p>
                <p className="text-xs">{lessonTitle}</p>
              </div>
              <div>
                <p className="text-muted-foreground text-xs">Subject</p>
                <p className="text-xs">{courseSubject}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};