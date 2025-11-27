import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
  BookOpen,
  Clock,
  Target,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Zap,
  Code,
  Brain,
  Lightbulb,
  ArrowRight,
  Download,
} from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

interface LessonDetailViewProps {
  lesson: {
    id: string;
    title: string;
    content: string;
    difficulty: string;
    duration: number;
    learning_objectives?: string[];
    prerequisites?: string[];
    assessment_questions?: any[];
    practice_exercises?: string[];
  };
  onComplete?: () => void;
  onStartQuiz?: () => void;
  courseProgress?: {
    completed_lessons: number;
    total_lessons: number;
  };
}

const DifficultyBadgeColor = {
  beginner: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
  intermediate: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100',
  advanced: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-100',
  expert: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100',
};

const MarkdownComponents = {
  h1: ({ node, ...props }: any) => (
    <h1 className="text-4xl font-bold mt-8 mb-4 text-gray-900 dark:text-white" {...props} />
  ),
  h2: ({ node, ...props }: any) => (
    <h2 className="text-3xl font-bold mt-6 mb-3 text-gray-800 dark:text-gray-100 border-l-4 border-blue-500 pl-4" {...props} />
  ),
  h3: ({ node, ...props }: any) => (
    <h3 className="text-2xl font-semibold mt-5 mb-2 text-gray-700 dark:text-gray-200" {...props} />
  ),
  h4: ({ node, ...props }: any) => (
    <h4 className="text-xl font-semibold mt-4 mb-2 text-gray-600 dark:text-gray-300" {...props} />
  ),
  h5: ({ node, ...props }: any) => (
    <h5 className="text-lg font-semibold mt-3 mb-1 text-gray-600 dark:text-gray-300" {...props} />
  ),
  p: ({ node, ...props }: any) => (
    <p className="text-base leading-7 mb-4 text-gray-700 dark:text-gray-300" {...props} />
  ),
  ul: ({ node, ...props }: any) => (
    <ul className="list-disc list-inside space-y-2 mb-4 ml-4 text-gray-700 dark:text-gray-300" {...props} />
  ),
  ol: ({ node, ...props }: any) => (
    <ol className="list-decimal list-inside space-y-2 mb-4 ml-4 text-gray-700 dark:text-gray-300" {...props} />
  ),
  li: ({ node, ...props }: any) => (
    <li className="mb-2" {...props} />
  ),
  code: ({ node, inline, ...props }: any) => {
    if (inline) {
      return (
        <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm font-mono text-red-600 dark:text-red-400" {...props} />
      );
    }
    return <code className="bg-gray-100 dark:bg-gray-800 p-4 rounded text-sm font-mono overflow-x-auto block" {...props} />;
  },
  pre: ({ node, ...props }: any) => (
    <pre className="bg-gray-900 dark:bg-gray-950 text-gray-100 p-4 rounded-lg overflow-x-auto mb-4" {...props} />
  ),
  blockquote: ({ node, ...props }: any) => (
    <blockquote className="border-l-4 border-blue-500 pl-4 italic my-4 text-gray-600 dark:text-gray-400" {...props} />
  ),
  table: ({ node, ...props }: any) => (
    <div className="overflow-x-auto my-4">
      <table className="w-full border-collapse border border-gray-300 dark:border-gray-700" {...props} />
    </div>
  ),
  th: ({ node, ...props }: any) => (
    <th className="border border-gray-300 dark:border-gray-700 bg-gray-100 dark:bg-gray-800 px-4 py-2 text-left" {...props} />
  ),
  td: ({ node, ...props }: any) => (
    <td className="border border-gray-300 dark:border-gray-700 px-4 py-2" {...props} />
  ),
};

export const LessonDetailView: React.FC<LessonDetailViewProps> = ({
  lesson,
  onComplete,
  onStartQuiz,
  courseProgress,
}) => {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));
  const [completedExercises, setCompletedExercises] = useState<Set<string>>(new Set());

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const markExerciseComplete = (exerciseId: string) => {
    const newCompleted = new Set(completedExercises);
    newCompleted.add(exerciseId);
    setCompletedExercises(newCompleted);
    toast({
      title: '✅ Exercise Completed!',
      description: 'Great job! Keep going.',
    });
  };

  const handleDownload = () => {
    try {
      // Create content with title and markdown
      const fullContent = `# ${lesson.title}\n\n**Difficulty:** ${lesson.difficulty}\n**Duration:** ${lesson.duration} minutes\n\n${lesson.content}`;
      
      // Create blob and download
      const element = document.createElement('a');
      const file = new Blob([fullContent], { type: 'text/markdown' });
      element.href = URL.createObjectURL(file);
      element.download = `${lesson.title.replace(/\s+/g, '_')}.md`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
      
      toast({
        title: '✅ Downloaded',
        description: 'Lesson content downloaded as Markdown file',
      });
    } catch (error) {
      toast({
        title: '❌ Error',
        description: 'Failed to download lesson',
        variant: 'destructive',
      });
    }
  };

  const completionPercentage = courseProgress
    ? Math.round((courseProgress.completed_lessons / courseProgress.total_lessons) * 100)
    : 0;

  const getDifficultyColor = (difficulty: string) => {
    return (
      DifficultyBadgeColor[difficulty as keyof typeof DifficultyBadgeColor] ||
      'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100'
    );
  };

  return (
    <div className="w-full max-w-6xl mx-auto px-4 py-6 space-y-6">
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4"
      >
        {/* Course Progress */}
        {courseProgress && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Course Progress</span>
              <span className="text-muted-foreground">
                {courseProgress.completed_lessons} of {courseProgress.total_lessons} lessons
              </span>
            </div>
            <Progress value={completionPercentage} className="h-2" />
          </div>
        )}

        {/* Lesson Title & Metadata */}
        <div className="space-y-3">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="flex-1">
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-3">
                {lesson.title}
              </h1>
              <div className="flex items-center gap-3 flex-wrap">
                <Badge className={getDifficultyColor(lesson.difficulty)}>
                  {lesson.difficulty.charAt(0).toUpperCase() + lesson.difficulty.slice(1)}
                </Badge>
                <div className="flex items-center gap-1 text-gray-600 dark:text-gray-400">
                  <Clock className="h-4 w-4" />
                  <span>{lesson.duration} minutes</span>
                </div>
              </div>
            </div>
            <motion.div
              className="flex gap-2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <Button
                onClick={onStartQuiz}
                disabled={!lesson.assessment_questions?.length}
                className="gap-2"
              >
                <Brain className="h-4 w-4" />
                Take Quiz
              </Button>
              <Button
                onClick={onComplete}
                variant="outline"
                className="gap-2"
              >
                <CheckCircle2 className="h-4 w-4" />
                Complete
              </Button>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Main Content Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 gap-2 lg:gap-0">
            <TabsTrigger value="overview" className="gap-2 text-sm">
              <BookOpen className="h-4 w-4" />
              <span className="hidden sm:inline">Overview</span>
            </TabsTrigger>
            <TabsTrigger value="content" className="gap-2 text-sm">
              <Zap className="h-4 w-4" />
              <span className="hidden sm:inline">Content</span>
            </TabsTrigger>
            <TabsTrigger value="questions" disabled={!lesson.assessment_questions?.length} className="gap-2 text-sm">
              <Brain className="h-4 w-4" />
              <span className="hidden sm:inline">Quiz</span>
            </TabsTrigger>
            <TabsTrigger value="exercises" disabled={!lesson.practice_exercises?.length} className="gap-2 text-sm">
              <Code className="h-4 w-4" />
              <span className="hidden sm:inline">Exercises</span>
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6 mt-6">
            {/* Learning Objectives */}
            {lesson.learning_objectives && lesson.learning_objectives.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="h-5 w-5 text-green-500" />
                      Learning Objectives
                    </CardTitle>
                    <CardDescription>
                      What you'll be able to do by the end of this lesson
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3">
                      {lesson.learning_objectives.map((objective, idx) => (
                        <motion.li
                          key={idx}
                          className="flex items-start gap-3"
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.05 }}
                        >
                          <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-gray-700 dark:text-gray-300">{objective}</span>
                        </motion.li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {/* Prerequisites */}
            {lesson.prerequisites && lesson.prerequisites.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertCircle className="h-5 w-5 text-blue-500" />
                      Prerequisites
                    </CardTitle>
                    <CardDescription>
                      What you should know before starting this lesson
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {lesson.prerequisites.map((prereq, idx) => (
                        <li key={idx} className="flex items-start gap-3 text-gray-700 dark:text-gray-300">
                          <ArrowRight className="h-4 w-4 text-blue-500 flex-shrink-0 mt-1" />
                          {prereq}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </TabsContent>

          {/* Content Tab */}
          <TabsContent value="content" className="space-y-6 mt-6">
            <Card className="overflow-hidden">
              <CardContent className="pt-6">
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeRaw]}
                    components={MarkdownComponents}
                  >
                    {lesson.content}
                  </ReactMarkdown>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Quiz Tab */}
          <TabsContent value="questions" className="space-y-6 mt-6">
            {lesson.assessment_questions && lesson.assessment_questions.length > 0 ? (
              <div className="space-y-4">
                {lesson.assessment_questions.map((question, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                  >
                    <Card className="cursor-pointer hover:shadow-md transition-shadow">
                      <CardHeader>
                        <CardTitle className="text-lg">
                          Question {idx + 1}: {question.question || `Assessment ${idx + 1}`}
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        {question.options && (
                          <div className="space-y-3">
                            {question.options.map((option: string, optIdx: number) => (
                              <label
                                key={optIdx}
                                className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                              >
                                <input
                                  type="radio"
                                  name={`question-${idx}`}
                                  value={optIdx}
                                  className="h-4 w-4"
                                />
                                <span className="text-gray-700 dark:text-gray-300">{option}</span>
                              </label>
                            ))}
                          </div>
                        )}
                        {!question.options && (
                          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                            <p className="text-gray-600 dark:text-gray-400 text-sm">
                              Answer: {question.answer || 'Check with instructor'}
                            </p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: lesson.assessment_questions.length * 0.1 }}
                >
                  <Button onClick={onStartQuiz} className="w-full gap-2" size="lg">
                    <Brain className="h-4 w-4" />
                    Submit Quiz
                  </Button>
                </motion.div>
              </div>
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-center text-gray-500 dark:text-gray-400">
                    No assessment questions available for this lesson
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Exercises Tab */}
          <TabsContent value="exercises" className="space-y-6 mt-6">
            {lesson.practice_exercises && lesson.practice_exercises.length > 0 ? (
              <div className="space-y-4">
                {lesson.practice_exercises.map((exercise, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                  >
                    <Card
                      className="cursor-pointer hover:shadow-md transition-all"
                      onClick={() => toggleSection(`exercise-${idx}`)}
                    >
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-lg flex items-center gap-3 flex-1">
                            <Code className="h-5 w-5 text-blue-500" />
                            Exercise {idx + 1}
                            {completedExercises.has(`exercise-${idx}`) && (
                              <CheckCircle2 className="h-5 w-5 text-green-500 ml-auto" />
                            )}
                          </CardTitle>
                          {expandedSections.has(`exercise-${idx}`) ? (
                            <ChevronUp className="h-5 w-5" />
                          ) : (
                            <ChevronDown className="h-5 w-5" />
                          )}
                        </div>
                      </CardHeader>

                      <AnimatePresence>
                        {expandedSections.has(`exercise-${idx}`) && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                          >
                            <CardContent className="space-y-4">
                              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                                <ReactMarkdown
                                  remarkPlugins={[remarkGfm]}
                                  rehypePlugins={[rehypeRaw]}
                                  components={MarkdownComponents}
                                >
                                  {exercise}
                                </ReactMarkdown>
                              </div>

                              <Button
                                onClick={() => markExerciseComplete(`exercise-${idx}`)}
                                disabled={completedExercises.has(`exercise-${idx}`)}
                                className="w-full gap-2"
                              >
                                {completedExercises.has(`exercise-${idx}`) ? (
                                  <>
                                    <CheckCircle2 className="h-4 w-4" />
                                    Completed
                                  </>
                                ) : (
                                  <>
                                    <CheckCircle2 className="h-4 w-4" />
                                    Mark as Complete
                                  </>
                                )}
                              </Button>
                            </CardContent>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </Card>
                  </motion.div>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-center text-gray-500 dark:text-gray-400">
                    No practice exercises available for this lesson
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </motion.div>

      {/* Action Footer */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="flex gap-3 sticky bottom-4 bg-white dark:bg-gray-950 p-4 rounded-lg shadow-lg"
      >
        <Button onClick={onComplete} className="flex-1 gap-2">
          <CheckCircle2 className="h-4 w-4" />
          Mark as Complete
        </Button>
        <Button
          onClick={onStartQuiz}
          disabled={!lesson.assessment_questions?.length}
          variant="outline"
          className="flex-1 gap-2"
        >
          <Brain className="h-4 w-4" />
          Test Knowledge
        </Button>
        <Button onClick={handleDownload} variant="ghost" className="gap-2">
          <Download className="h-4 w-4" />
          <span className="hidden sm:inline">Download</span>
        </Button>
      </motion.div>
    </div>
  );
};
