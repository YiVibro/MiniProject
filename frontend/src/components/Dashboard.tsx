import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Plus, BookOpen, Target, TrendingUp, Clock, Award, Sparkles, ArrowRight, Loader2 } from "lucide-react";
import { CreateGoalDialog } from "./CreateGoalDialog";
import { useAuth } from "../store/AuthContext";
import { supabase } from "../lib/supabaseClient";
import { ChatView } from "./ChatView";
import { QuizView } from "./QuizView";
import { PDFUploadCard } from "./PDFUploadCard";
import { agentService } from "../lib/agentService";
import { useToast } from "@/components/ui/use-toast";
import DynamicCourseGenerator from "./DynamicCourseGenerator";
import { CourseLearnView } from "./CourseLearnView";
import { LearningPathView } from "./LearningPathView";

export const Dashboard = () => {
  const [showCreateGoal, setShowCreateGoal] = useState(false);
  const { user } = useAuth();
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showQuizGenerationDialog, setShowQuizGenerationDialog] = useState(false);
  const [currentQuizId, setCurrentQuizId] = useState<number | null>(null);
  const [latestDoc, setLatestDoc] = useState<any>(null);
  const [view, setView] = useState<"dashboard" | "learn" | "quiz" | "learning-path" | "courses">("dashboard");
  const [isContinuing, setIsContinuing] = useState(false);
  const [courseLoadingStates, setCourseLoadingStates] = useState<Record<string, boolean>>({});
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [currentCourseName, setCurrentCourseName] = useState<string | null>(null);
  const [currentCourseId, setCurrentCourseId] = useState<string | null>(null);
  const { toast } = useToast();
  const [currentCourseData, setCurrentCourseData] = useState<any>(null);
  const [coursesWithGeneration, setCoursesWithGeneration] = useState<Set<string>>(new Set());

  // ✅ ADD: Function to check if course exists in DB
  const checkCourseExists = async (userId: string, courseName: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/agents/check-course-exists`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, course_name: courseName })
      });

      const data = await response.json();
      return data.exists;
    } catch (error) {
      console.error('Error checking course existence:', error);
      return false;
    }
  };

  // ✅ ADD: useEffect to check courses on load
  useEffect(() => {
    const checkExistingCourses = async () => {
      if (!user?.id || !courses) return;

      const existingCourses = new Set<string>();

      for (const course of courses) {
        const exists = await checkCourseExists(user.id, course.title);
        if (exists) {
          existingCourses.add(course.title);
        }
      }

      setCoursesWithGeneration(existingCourses);
    };

    checkExistingCourses();
  }, [user?.id, courses]);

  // ✅ ADD: Helper functions for button text and icon
  const getButtonText = (courseTitle: string) => {
    return coursesWithGeneration.has(courseTitle) ? 'Continue Learning' : 'Generate Course';
  };

  const getButtonIcon = (courseTitle: string) => {
    return coursesWithGeneration.has(courseTitle) ? <ArrowRight className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />;
  };

  const fetchCourses = async () => {
    if (!user) return;

    try {
      setLoading(true);
      const { data, error } = await supabase
        .from("user_progress")
        .select(`
          id, 
          course_name, 
          progress_percent, 
          category_id,
          categories!inner(name)
        `)
        .eq("user_id", user.id);

      if (error) throw error;

      const formattedCourses = data.map((course: any) => ({
        id: course.id,
        title: course.course_name,
        subject: course.categories?.name || `Category ${course.category_id?.slice(0, 4) || 'General'}`,
        progress: course.progress_percent || 0,
        description: `Continue your learning journey`,
        totalLessons: 10,
        completedLessons: Math.round(((course.progress_percent || 0) / 100) * 10),
        goalType: "Learning Goal",
        dueDate: "2024-12-31"
      }));

      setCourses(formattedCourses);
    } catch (error: any) {
      console.error("Error fetching courses:", error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchLatestDocument = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/pdf/documents?limit=1");
      if (!res.ok) throw new Error("Failed to fetch documents");
      const docs = await res.json();
      if (docs.length > 0) {
        setLatestDoc(docs[0]);
      }
    } catch (err) {
      console.error("Error fetching documents:", err);
    }
  };

  useEffect(() => {
    if (user) {
      fetchCourses();
      fetchLatestDocument();
    }
  }, [user]);

  useEffect(() => {
    if (!user) return;

    const subscription = supabase
      .channel('user_progress_updates')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'user_progress',
          filter: `user_id=eq.${user.id}`
        },
        () => {
          fetchCourses();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(subscription);
    };
  }, [user]);

  const handleGoalCreated = () => {
    fetchCourses();
    setShowCreateGoal(false);
  };

  const handleUploadComplete = () => {
    setShowQuizGenerationDialog(true);
  };

  const handleGeneratePlan = async (courseName: string) => {
    if (!user) return;

    try {
      const plan = await agentService.createLearningPlan({
        user_id: user.id,
        user_request: `I want to learn ${courseName}`,
        preferences: {}
      });

      toast({
        title: "Learning Plan Created! 🎉",
        description: `Your personalized ${courseName} course is ready!`,
      });

      await fetchCourses(); // Refresh courses after plan creation
    } catch (error: any) {
      console.error('Error generating plan:', error);
      toast({
        title: "Generation Failed",
        description: error.message || "Failed to create learning plan. Please try again.",
        variant: "destructive",
      });
    }
  };

  // ✅ UPDATED: handleContinueLearning with button state management
  const handleContinueLearning = async (course: any) => {
    console.log('handleContinueLearning called with course:', course);
    console.log('Current user:', user);

    if (!user) {
      console.error('User is null in handleContinueLearning');
      toast({
        title: "Authentication Required",
        description: "Please log in to continue learning.",
        variant: "destructive",
      });
      return;
    }

    if (!user.id) {
      console.error('User ID is missing:', user);
      toast({
        title: "Authentication Error",
        description: "User information is incomplete. Please log in again.",
        variant: "destructive",
      });
      return;
    }

    try {

      //setIsContinuing(true);
      setCourseLoadingStates(prev => ({ ...prev, [course.id]: true }));
      console.log('Continuing learning for course:', course.title);


      // Validate course data
      if (!course.id && !course.title) {
        toast({
          title: "Invalid Course",
          description: "Course information is missing. Please try again.",
          variant: "destructive",
        });
        return;
      }

      // Prepare request payload - only include defined values
      const requestPayload: any = {
        user_id: user.id
      };

      // Convert course.id to string if it exists (it might be a number from DB)
      if (course.id !== undefined && course.id !== null) {
        requestPayload.course_id = String(course.id);
      }

      if (course.title) {
        requestPayload.course_name = String(course.title);
      } else if (course.course_name) {
        requestPayload.course_name = String(course.course_name);
      } else if (course.name) {
        requestPayload.course_name = String(course.name);
      } else {
        // Fallback - use the first part of the ID or a default name
        requestPayload.course_name = `Course-${course.id || 'default'}`;
      }
      console.log('Sending continue-learning request:', requestPayload);

      // Call the new continue-learning endpoint
      const response = await agentService.continueLearning(requestPayload);

      console.log('Continue learning response:', response);

      // ✅ FIX: Store complete course data in sessionStorage with proper structure
      const courseData = {
        course_id: response.course_id || course.id, // Fallback to course.id if response doesn't have course_id
        curriculum: response.curriculum || [], // ✅ Ensure curriculum is always an array
        progress: response.progress || { // ✅ Ensure progress has proper structure
          progress_percent: 0,
          completed_lessons: 0,
          total_lessons: response.curriculum?.length || 0,
          current_lesson: 1
        },
        learning_path: response.learning_path || {}, // ✅ Ensure learning_path exists
        requirements: response.requirements || {}, // ✅ Store requirements
        title: course.title,
        subject: course.subject || 'General', // ✅ Fallback subject
        // ✅ ADD: Include any additional metadata that might be useful
        metadata: {
          is_cached: response.is_cached || false,
          learning_goal_id: response.learning_goal_id,
          generated_at: new Date().toISOString()
        }
      };

      console.log('Storing course data in sessionStorage:', courseData);

      // ✅ Store the complete course data
      sessionStorage.setItem('currentCourseData', JSON.stringify(courseData));

      // ✅ UPDATE: Mark course as existing in DB for button state
      setCoursesWithGeneration(prev => new Set([...prev, course.title]));

      // Also store individual pieces for easy access
      setCurrentCourseName(course.title);
      setCurrentCourseId(courseData.course_id);

      // ✅ Store course data in state as well for immediate access
      setCurrentCourseData(courseData);

      // Navigate to learning path view
      setView("learning-path");

      toast({
        title: courseData.progress.completed_lessons > 0 ? "Welcome Back! 🎉" : "Course Generated! 🎉",
        description: courseData.progress.completed_lessons > 0
          ? `Continuing your ${course.title} journey...`
          : `Your personalized ${course.title} course is ready!`,
      });

    } catch (error: any) {
      console.error("Error continuing learning:", error);

      // Handle FastAPI validation errors (422)
      let errorMessage = "Failed to continue learning. Please try again.";
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          // Format validation errors
          errorMessage = detail.map((err: any) =>
            `${err.loc?.join('.')}: ${err.msg}`
          ).join(', ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else {
          errorMessage = JSON.stringify(detail);
        }
      } else if (error.message) {
        errorMessage = error.message;
      }

      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      //setIsContinuing(false);
      setCourseLoadingStates(prev => ({ ...prev, [course.id]: false }));
    }
  };

  // Learning path view
  // In your Dashboard's render method, update the LearningPathView component:
  if (view === "learning-path") {
    return (
      <LearningPathView
        courseId={currentCourseId}
        courseTitle={currentCourseName}
        courseSubject={currentCourseData?.subject || 'General'}
        // ✅ Pass the course data directly as a prop if needed
        courseData={currentCourseData}
        onBack={() => setView("courses")}
      />
    );
  }

  if (view === "learn") {
    return (
      <CourseLearnView
        sessionId={currentSessionId}
        lessonId={`lesson_${currentCourseName?.toLowerCase().replace(/\s+/g, '_')}`}
        lessonTitle={currentCourseName || ''}
        courseSubject={courses.find(c => c.title === currentCourseName)?.subject || ''}
        onBack={() => {
          setView("dashboard");
          setCurrentSessionId(null);
          setCurrentCourseName(null);
          fetchCourses(); // Refresh courses to show updated progress
        }}
      />
    );
  }

  if (view === "quiz" && currentQuizId) {
    return (
      <QuizView
        quizId={currentQuizId}
        onBack={() => setView("dashboard")}
      />
    );
  }

  const todayTasks = [
    { task: "Complete Calculus Chapter 5", subject: "Mathematics", urgent: true },
    { task: "Review Newton's Laws", subject: "Physics", urgent: false },
    { task: "Practice Chemical Equations", subject: "Chemistry", urgent: false },
    { task: "AI Generated Quiz - Algebra", subject: "Mathematics", urgent: true },
  ];

  const fadeInUp = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  const cardClasses = "bg-card border border-border shadow-lg rounded-2xl transition-all duration-300";
  const innerCardClasses = "p-4 bg-card/5 backdrop-blur-sm rounded-xl border border-border hover:bg-card/10 transition-all duration-300";

  return (
    <div className="min-h-screen bg-background text-foreground font-sans p-6 space-y-6 transition-colors duration-500">

      <motion.div
        initial="hidden"
        animate="visible"
        variants={fadeInUp}
        transition={{ duration: 0.6 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold">Welcome back, {user?.user_metadata?.full_name || 'Student'}!</h1>
          <p className="text-muted-foreground mt-1">
            Ready to continue your learning journey?
          </p>
        </div>
        <Button
          className="gap-2 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-purple-500 hover:to-blue-500 text-white"
          onClick={() => setShowCreateGoal(true)}
        >
          <Plus className="w-4 h-4" />
          Create New Goal
        </Button>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { icon: BookOpen, label: "Active Courses", value: courses.length, color: "from-blue-500 to-blue-700" },
          { icon: Target, label: "Goals Achieved", value: "8", color: "from-green-500 to-green-700" },
          { icon: TrendingUp, label: "Avg Progress", value: `${courses.length > 0 ? Math.round(courses.reduce((acc, course) => acc + course.progress, 0) / courses.length) : 0}%`, color: "from-purple-500 to-purple-700" },
          { icon: Clock, label: "Study Streak", value: "24h", color: "from-orange-500 to-orange-700" },
        ].map((stat, i) => (
          <motion.div
            key={i}
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            transition={{ duration: 0.5, delay: i * 0.1 }}
          >
            <Card className={cardClasses}>
              <CardContent className="p-6 flex items-center gap-4">
                <div className={`p-3 rounded-xl bg-gradient-to-r ${stat.color} shadow-lg text-white`}>
                  <stat.icon className="w-6 h-6" />
                </div>
                <div>
                  <div className="text-2xl font-semibold">{stat.value}</div>
                  <div className="text-sm text-muted-foreground">{stat.label}</div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          transition={{ duration: 0.6 }}
          className="lg:col-span-2"
        >
          <Card className={cardClasses}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="w-5 h-5" />
                Your Active Courses
                {loading && <Badge variant="secondary">Loading...</Badge>}
              </CardTitle>
              <CardDescription className="text-muted-foreground">
                Continue where you left off
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  <p className="text-muted-foreground mt-2">Loading courses...</p>
                </div>
              ) : courses.length === 0 ? (
                <div className="text-center py-8">
                  <BookOpen className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No active courses</h3>
                  <p className="text-muted-foreground mb-4">
                    Create your first learning goal to get started
                  </p>
                  <Button
                    onClick={() => setShowCreateGoal(true)}
                    className="gap-2"
                  >
                    <Plus className="w-4 h-4" />
                    Create Goal
                  </Button>
                </div>
              ) : (
                courses.map((course, index) => (
                  <motion.div
                    key={course.id}
                    className={innerCardClasses}
                    initial="hidden"
                    animate="visible"
                    variants={fadeInUp}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">{course.title}</h3>
                        <p className="text-sm text-muted-foreground">{course.subject}</p>
                      </div>
                      <Badge variant="secondary">{course.goalType}</Badge>
                    </div>

                    <div className="space-y-2 mt-2">
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>Progress</span>
                        <span>{course.progress}%</span>
                      </div>
                      <Progress value={course.progress} className="h-2 rounded-full bg-border" />
                    </div>

                    <div className="flex items-center justify-between text-sm text-muted-foreground mt-1">
                      <span>
                        {course.completedLessons}/{course.totalLessons} lessons
                      </span>
                      <span>Due: {course.dueDate}</span>
                    </div>

                    <div className="mt-2">
                      <Button
                        variant={coursesWithGeneration.has(course.title) ? "default" : "outline"}
                        size="sm"
                        className="w-full gap-2"
                        onClick={() => handleContinueLearning(course)}
                        disabled={courseLoadingStates[course.id] || false}
                      >
                        {courseLoadingStates[course.id] ? (
                          <>
                            <Loader2 className="h-4 w-4 animate-spin" />
                            {coursesWithGeneration.has(course.title) ? 'Loading...' : 'Generating...'}
                          </>
                        ) : (
                          <>
                            {getButtonIcon(course.title)}
                            {getButtonText(course.title)}
                          </>
                        )}
                      </Button>
                    </div>
                  </motion.div>
                ))
              )}
            </CardContent>
          </Card>
        </motion.div>

        <div className="space-y-6">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
          >
            <Card className={cardClasses}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="w-5 h-5" />
                  Today's Tasks
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  Stay on track with your goals
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {todayTasks.map((task, index) => (
                  <motion.div
                    key={index}
                    className="flex items-start gap-3 p-3 rounded-xl bg-card/5 border border-border hover:bg-card/10 transition-colors"
                    initial="hidden"
                    animate="visible"
                    variants={fadeInUp}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                  >
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium">{task.task}</p>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">{task.subject}</Badge>
                        {task.urgent && (
                          <Badge variant="destructive" className="text-xs">Urgent</Badge>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          <PDFUploadCard onUploadComplete={handleUploadComplete} />
        </div>
      </div>

      <CreateGoalDialog
        open={showCreateGoal}
        onOpenChange={setShowCreateGoal}
        onGoalCreated={handleGoalCreated}
      />
    </div>
  );
};