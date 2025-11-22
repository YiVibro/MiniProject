// frontend/src/components/LearningPathView.tsx
import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useLearningPath } from './hooks/useLearningPath';
import { LessonNode } from './LessonNode';
import { AssessmentDialog } from './AssessmentDialog';
import { GapAnalysisPanel } from './GapAnalysisPanel';
import { 
  ArrowLeft, 
  BookOpen, 
  Target, 
  Trophy, 
  Sparkles, 
  Clock,
  ChevronRight,
  CheckCircle2,
  AlertTriangle,
  Play,
  FileText,
  HelpCircle
} from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { useNavigate, useParams } from 'react-router-dom';
import { agentService } from '@/lib/agentService';
import { LessonContentView } from './LessonContentView';

interface LearningPathViewProps {
  courseId?: string;
  courseTitle?: string;
  courseSubject?: string;
  courseData?: any;
  onBack?: () => void;
}

interface Lesson {
  id: string;
  title: string;
  content: string;
  difficulty: string;
  duration: number;
  learning_objectives: string[];
  prerequisites: string[];
  assessment_questions?: any[];
  practice_exercises?: any[];
  subtopics?: Array<{
    title: string;
    content: string;
    duration_minutes: number;
  }>;
  questions?: Array<{
    id: string;
    question: string;
    type: string;
    options?: string[];
  }>;
}

// ✅ FIXED: Make progress optional in CourseData interface
interface CourseData {
  course_id: string;
  curriculum: Lesson[];
  progress?: {  // Made optional with ?
    progress_percent: number;
    completed_lessons: number;
    total_lessons: number;
    current_lesson: number;
  };
  requirements: any;
  learning_path: any;
}

export const LearningPathView: React.FC<LearningPathViewProps> = (props) => {
  const routerParams = useParams();
  const navigate = useNavigate();
  
  const courseId = props.courseId || routerParams.courseId || '';
  const courseTitle = props.courseTitle || 'Your Course';
  const courseSubject = props.courseSubject || 'General';
  
  console.log('LearningPathView - Course ID:', courseId);
  console.log('LearningPathView - Props:', props);

  const {
    data,
    currentLesson,
    assessment,
    assessmentResults,
    isLoading,
    isAssessing,
    progress,
    loadLearningPath,
    startLesson,
    completeLesson,
    startAssessment,
    submitAssessment,
    unlockNextNode
  } = useLearningPath();

  const [activeTab, setActiveTab] = useState<'path' | 'content' | 'analytics'>('path');
  const [showAssessment, setShowAssessment] = useState(false);
  const [showGapAnalysis, setShowGapAnalysis] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [courseData, setCourseData] = useState<CourseData | null>(null);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [currentProgress, setCurrentProgress] = useState({
    progress_percent: 0,
    completed_lessons: 0,
    total_lessons: 0,
    current_lesson: 1
  });
  const { toast } = useToast();

  // ✅ FETCH COURSE DATA FROM BACKEND
  useEffect(() => {
    const loadCourseData = async () => {
      try {
        console.log('Loading course data for ID:', courseId);
        
        // ✅ GET COURSE DATA FROM BACKEND
        let courseData: CourseData;
        
        // First check sessionStorage
        const courseDataStr = sessionStorage.getItem('currentCourseData');
        if (courseDataStr) {
          courseData = JSON.parse(courseDataStr);
          console.log('Found course data in sessionStorage:', courseData);
        } else if (courseId) {
          // Fetch from backend API
          console.log('Fetching course data from backend...');
          // ✅ FIXED: Use the correct service method based on your API
          const response = await agentService.continueLearning({
            user_id: 'current-user', // You'll need to get this from auth context
            course_id: courseId
          });
          courseData = response;
          console.log('Course data from backend:', courseData);
        } else {
          throw new Error('Course ID is required');
        }

        // ✅ POPULATE STATE WITH COURSE DATA
        setCourseData(courseData);
        setLessons(courseData.curriculum || []);
        
        // ✅ FIXED: Handle optional progress with fallback
        const courseProgress = courseData.progress || {
          progress_percent: 0,
          completed_lessons: 0,
          total_lessons: courseData.curriculum?.length || 0,
          current_lesson: 1
        };
        setCurrentProgress(courseProgress);

        // ✅ TRANSFORM CURRICULUM TO LEARNING PATH NODES
        const nodes = (courseData.curriculum || []).map((lesson: Lesson, index: number) => ({
          id: lesson.id,
          title: lesson.title,
          description: lesson.content?.substring(0, 150) + '...' || 'Lesson content',
          type: 'lesson' as const,
          status: index === 0 ? 'current' as const : 'locked' as const,
          difficulty: lesson.difficulty,
          duration: lesson.duration,
          prerequisites: lesson.prerequisites || [],
          metadata: {
            learning_objectives: lesson.learning_objectives || [],
            content: lesson.content,
            subtopics: lesson.subtopics || [],
            questions: lesson.questions || lesson.assessment_questions || [],
            practice_exercises: lesson.practice_exercises || []
          }
        }));

        // ✅ FIXED: Call loadLearningPath with just the courseId string
        // Remove the object parameter and just pass the courseId
        if (loadLearningPath && typeof loadLearningPath === 'function') {
          await loadLearningPath(courseId); // Just pass the string
        }

        toast({
          title: 'Course Loaded',
          description: `Successfully loaded ${courseData.curriculum?.length || 0} lessons`,
        });

      } catch (error) {
        console.error('Error loading course data:', error);
        setError('Failed to load course data. Please try again.');
        toast({
          title: 'Error',
          description: 'Failed to load course content',
          variant: 'destructive'
        });
      }
    };

    if (courseId) {
      loadCourseData();
    }
  }, [courseId, loadLearningPath, toast]);

  const handleBack = () => {
    if (props.onBack) {
      props.onBack();
    } else {
      navigate(-1);
    }
  };

  const handleStartLesson = async (nodeId: string) => {
    await startLesson(nodeId);
    setActiveTab('content');
  };

  const handleCompleteLesson = async (nodeId: string) => {
    await completeLesson(nodeId);
    
    // Update local progress state
    const lessonIndex = lessons.findIndex(lesson => lesson.id === nodeId);
    if (lessonIndex !== -1) {
      const newCompleted = currentProgress.completed_lessons + 1;
      const newProgress = {
        ...currentProgress,
        completed_lessons: newCompleted,
        progress_percent: (newCompleted / currentProgress.total_lessons) * 100,
        current_lesson: lessonIndex + 2 // Next lesson
      };
      setCurrentProgress(newProgress);
    }

    // Auto-start assessment after lesson completion
    setTimeout(async () => {
      await startAssessment(nodeId);
      setShowAssessment(true);
    }, 1000);
  };

  const handleAssessmentComplete = async (answers: Record<string, any>) => {
    await submitAssessment(answers);
    setShowAssessment(false);
    
    if (assessmentResults?.passed) {
      setTimeout(() => {
        unlockNextNode();
        setShowGapAnalysis(true);
      }, 1500);
    } else {
      setShowGapAnalysis(true);
    }
  };

  const handleCloseGapAnalysis = () => {
    setShowGapAnalysis(false);
    if (assessmentResults?.passed) {
      toast({
        title: 'Ready for next lesson!',
        description: 'Congratulations on completing this module!',
      });
    }
  };

    // Add error state display
  if (error) {
    return (
      <div className="min-h-screen bg-background p-6 flex items-center justify-center">
        <Card className="w-full max-w-2xl">
          <CardContent className="p-8 text-center">
            <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Error Loading Learning Path</h3>
            <p className="text-muted-foreground mb-4">{error}</p>
            <Button onClick={handleBack}>
              Go Back
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background p-6 flex items-center justify-center">
        <Card className="w-full max-w-2xl">
          <CardContent className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <h3 className="text-lg font-semibold mb-2">Loading Your Learning Path</h3>
            <p className="text-muted-foreground">Preparing your personalized journey...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // // ✅ START QUIZ FUNCTION
  // const startQuiz = (questions: any[]) => {
  //   if (questions && questions.length > 0) {
  //     startAssessment(currentLesson?.id || '');
  //     setShowAssessment(true);
  //   } else {
  //     toast({
  //       title: 'No Questions Available',
  //       description: 'This lesson does not have any quiz questions yet.',
  //       variant: 'destructive'
  //     });
  //   }
  // };
  return (
    <div className="min-h-screen bg-background p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-6"
      >
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={handleBack}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{courseTitle}</h1>
            <p className="text-muted-foreground">{courseSubject} - Your personalized learning journey</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <Badge variant="secondary" className="flex items-center gap-1">
            <Sparkles className="h-3 w-3" />
            AI-Powered
          </Badge>
          <div className="text-right">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Progress value={currentProgress.progress_percent} className="w-24 h-2" />
              <span>{Math.round(currentProgress.progress_percent)}%</span>
            </div>
            <div className="text-xs text-muted-foreground">
              {currentProgress.completed_lessons} of {currentProgress.total_lessons} lessons
            </div>
          </div>
        </div>
      </motion.div>

      <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="path" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Learning Path
          </TabsTrigger>
          <TabsTrigger value="content" className="flex items-center gap-2" disabled={!currentLesson}>
            <BookOpen className="h-4 w-4" />
            Lesson Content
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <Trophy className="h-4 w-4" />
            Progress Analytics
          </TabsTrigger>
        </TabsList>

        {/* Learning Path Tab */}
        <TabsContent value="path" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Your Learning Journey</CardTitle>
              <CardDescription>
                Complete each lesson to unlock the next. Follow the recommended path for optimal learning.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data?.nodes && data.nodes.length > 0 ? (
                  data.nodes.map((node, index) => (
                    <LessonNode
                      key={node.id}
                      node={node}
                      index={index}
                      onStart={() => handleStartLesson(node.id)}
                      onComplete={() => handleCompleteLesson(node.id)}
                      isCurrent={node.id === data.current_node_id}
                    />
                  ))
                ) : (
                  // ✅ FALLBACK: RENDER LESSONS FROM COURSE DATA
                  lessons.map((lesson, index) => (
                    <Card key={lesson.id} className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground font-semibold">
                            {index + 1}
                          </div>
                          <div>
                            <h3 className="font-semibold">{lesson.title}</h3>
                            <p className="text-sm text-muted-foreground">
                              {lesson.content?.substring(0, 100)}...
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {lesson.duration} min
                          </Badge>
                          <Badge variant="secondary">{lesson.difficulty}</Badge>
                          <Button 
                            size="sm" 
                            onClick={() => handleStartLesson(lesson.id)}
                            className="gap-1"
                          >
                            <Play className="h-3 w-3" />
                            Start
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Lesson Content Tab - UPDATED TO USE LessonContentView */}
        <TabsContent value="content">
          <AnimatePresence mode="wait">
            {currentLesson ? (
              <motion.div
                key={currentLesson.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                {/* ✅ USE NEW COMPONENT */}
                <LessonContentView
                  lesson={currentLesson}
                  onComplete={() => handleCompleteLesson(currentLesson.id)}
                  onTakeQuiz={() => {
                    startAssessment(currentLesson.id);
                    setShowAssessment(true);
                  }}
                />
              </motion.div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Active Lesson</h3>
                  <p className="text-muted-foreground mb-4">
                    Select a lesson from the learning path to start learning.
                  </p>
                  <Button onClick={() => setActiveTab('path')}>
                    View Learning Path
                  </Button>
                </CardContent>
              </Card>
            )}
          </AnimatePresence>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Trophy className="h-5 w-5" />
                  Progress Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>Course Completion</span>
                    <span className="font-semibold">{Math.round(currentProgress.progress_percent)}%</span>
                  </div>
                  <Progress value={currentProgress.progress_percent} className="w-full" />
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="text-center p-3 bg-muted rounded-lg">
                      <div className="font-semibold text-2xl">
                        {currentProgress.completed_lessons}
                      </div>
                      <div className="text-muted-foreground">Completed</div>
                    </div>
                    <div className="text-center p-3 bg-muted rounded-lg">
                      <div className="font-semibold text-2xl">
                        {currentProgress.total_lessons - currentProgress.completed_lessons}
                      </div>
                      <div className="text-muted-foreground">Remaining</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {lessons
                    .filter((_, index) => index < currentProgress.completed_lessons)
                    .slice(-3)
                    .reverse()
                    .map(lesson => (
                      <div key={lesson.id} className="flex items-center gap-3 p-2 rounded-lg bg-muted">
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                        <div>
                          <div className="font-medium">{lesson.title}</div>
                          <div className="text-xs text-muted-foreground">Completed</div>
                        </div>
                      </div>
                    ))}
                  {currentProgress.completed_lessons === 0 && (
                    <p className="text-muted-foreground text-center py-4">
                      No completed lessons yet. Start your first lesson!
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Assessment Dialog */}
      <AssessmentDialog
        open={showAssessment}
        onOpenChange={setShowAssessment}
        assessment={assessment}
        onSubmit={handleAssessmentComplete}
        isSubmitting={isAssessing}
      />

      {/* Gap Analysis Panel */}
      <GapAnalysisPanel
        open={showGapAnalysis}
        onOpenChange={setShowGapAnalysis}
        results={assessmentResults}
        onContinue={handleCloseGapAnalysis}
      />
    </div>
  );
};