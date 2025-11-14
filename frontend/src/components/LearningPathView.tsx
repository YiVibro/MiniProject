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
  AlertTriangle
} from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { useNavigate, useParams } from 'react-router-dom';

interface LearningPathViewProps {
  courseId?: string;
  courseTitle?: string;
  courseSubject?: string;
  onBack?: () => void;
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
  const { toast } = useToast();

  useEffect(() => {
    console.log('LearningPathView useEffect - courseId:', courseId);
    if (courseId) {
      setError(null);
      loadLearningPath(courseId).catch(err => {
        console.error('Failed to load learning path:', err);
        setError('Failed to load learning path. Please try again.');
      });
    } else {
      // Try to get course_id from sessionStorage if available
      const courseDataStr = sessionStorage.getItem('currentCourseData');
      if (courseDataStr) {
        try {
          const courseData = JSON.parse(courseDataStr);
          loadLearningPath(courseData.course_id).catch(err => {
            console.error('Failed to load learning path:', err);
            setError('Failed to load learning path. Please try again.');
          });
        } catch (err) {
          setError('Course ID is missing');
        }
      } else {
        setError('Course ID is missing');
      }
    }
  }, [courseId, loadLearningPath]);

  const handleBack = () => {
    if (props.onBack) {
      props.onBack();
    } else {
      navigate(-1); // Go back in router history
    }
  };

  const handleStartLesson = async (nodeId: string) => {
    await startLesson(nodeId);
    setActiveTab('content');
  };

  const handleCompleteLesson = async (nodeId: string) => {
    await completeLesson(nodeId);
    
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
      // Unlock next node after successful assessment
      setTimeout(() => {
        unlockNextNode();
        setShowGapAnalysis(true);
      }, 1500);
    } else {
      // Show gap analysis for failed assessment
      setShowGapAnalysis(true);
    }
  };

  const handleCloseGapAnalysis = () => {
    setShowGapAnalysis(false);
    if (assessmentResults?.passed) {
      // Move to next lesson automatically
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
            <p className="text-muted-foreground">Your personalized learning journey</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <Badge variant="secondary" className="flex items-center gap-1">
            <Sparkles className="h-3 w-3" />
            AI-Powered
          </Badge>
          <div className="text-right">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Progress value={progress} className="w-24 h-2" />
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="text-xs text-muted-foreground">
              {data?.nodes.filter(n => n.status === 'completed').length || 0} of {data?.nodes.length || 0} modules
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
                Complete each module to unlock the next. Follow the recommended path for optimal learning.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data?.nodes.map((node, index) => (
                  <LessonNode
                    key={node.id}
                    node={node}
                    index={index}
                    onStart={() => handleStartLesson(node.id)}
                    onComplete={() => handleCompleteLesson(node.id)}
                    isCurrent={node.id === data.current_node_id}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Lesson Content Tab */}
        <TabsContent value="content">
          <AnimatePresence mode="wait">
            {currentLesson && (
              <motion.div
                key={currentLesson.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>{currentLesson.title}</CardTitle>
                        <CardDescription>{currentLesson.description}</CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {currentLesson.duration} min
                        </Badge>
                        <Badge variant="secondary">{currentLesson.difficulty}</Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="prose max-w-none">
                      <h3>Learning Objectives</h3>
                      <ul>
                        {currentLesson.metadata?.learning_objectives?.map((obj: string, i: number) => (
                          <li key={i}>{obj}</li>
                        )) || [
                          'Understand core concepts',
                          'Apply knowledge in practice',
                          'Prepare for assessment'
                        ].map((obj, i) => <li key={i}>{obj}</li>)}
                      </ul>
                      
                      <h3>Content</h3>
                      <div className="bg-muted p-4 rounded-lg">
                        {currentLesson.metadata?.content || (
                          <p>This is dynamic lesson content that would be generated by the AI tutoring system based on your learning style and progress.</p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => setActiveTab('path')}>
                        Back to Path
                      </Button>
                      <Button 
                        onClick={() => handleCompleteLesson(currentLesson.id)}
                        className="gap-2"
                      >
                        Complete Lesson
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
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
                    <span className="font-semibold">{Math.round(progress)}%</span>
                  </div>
                  <Progress value={progress} className="w-full" />
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="text-center p-3 bg-muted rounded-lg">
                      <div className="font-semibold text-2xl">
                        {data?.nodes.filter(n => n.status === 'completed').length || 0}
                      </div>
                      <div className="text-muted-foreground">Completed</div>
                    </div>
                    <div className="text-center p-3 bg-muted rounded-lg">
                      <div className="font-semibold text-2xl">
                        {data?.nodes.filter(n => n.status === 'current').length || 0}
                      </div>
                      <div className="text-muted-foreground">In Progress</div>
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
                  {data?.nodes
                    .filter(node => node.status === 'completed')
                    .slice(-3)
                    .reverse()
                    .map(node => (
                      <div key={node.id} className="flex items-center gap-3 p-2 rounded-lg bg-muted">
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                        <div>
                          <div className="font-medium">{node.title}</div>
                          <div className="text-xs text-muted-foreground">Completed</div>
                        </div>
                      </div>
                    )) || (
                      <p className="text-muted-foreground text-center py-4">
                        No completed modules yet
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