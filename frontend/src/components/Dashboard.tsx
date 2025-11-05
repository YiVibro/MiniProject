import { useState, useEffect } from "react"; 
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Plus, BookOpen, Target, TrendingUp, Clock, Award, Brain } from "lucide-react";
import { CreateGoalDialog } from "./CreateGoalDialog";
import { useAuth } from "../store/AuthContext";
import { supabase } from "../lib/supabaseClient";
import { ChatView } from "./ChatView";
import { QuizView } from "./QuizView";
import { PDFUploadCard } from "./PDFUploadCard";
import { agentService } from "../lib/agentService";
import { useToast } from "@/components/ui/use-toast";

export const Dashboard = () => {
  const [showCreateGoal, setShowCreateGoal] = useState(false);
  const { user } = useAuth();
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(false); 
  const [showQuizGenerationDialog, setShowQuizGenerationDialog] = useState(false);
  const [currentQuizId, setCurrentQuizId] = useState<number | null>(null);
  const [latestDoc, setLatestDoc] = useState<any>(null);
  const [view, setView] = useState<"dashboard" | "chat" | "quiz">("dashboard");
  const [isContinuing, setIsContinuing] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [currentCourseName, setCurrentCourseName] = useState<string | null>(null);
  const { toast } = useToast();

  // ✅ FIXED: Properly defined fetchCourses with category join
  const fetchCourses = async () => {
    if (!user) return;

    try {
      setLoading(true);

      // ✅ FIXED: Join with categories table to get proper subject names
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

      console.log("Fetched courses:", data); // Debug log

      const formattedCourses = data.map((course: any) => ({
        id: course.id,
        title: course.course_name,
        subject: course.categories?.name || `Category ${course.category_id?.slice(0, 4) || 'General'}`,
        progress: course.progress_percent || 0,
        description: `Continue your learning journey`,
        totalLessons: 10,
        completedLessons: Math.round(((course.progress_percent || 0) / 100) * 10),
        goalType: "Learning Goal", // ✅ FIXED: Added missing goalType
        dueDate: "2024-12-31" // ✅ FIXED: Added missing dueDate
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

  // ✅ FIXED: Added real-time subscription with proper cleanup
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
          console.log("Real-time update received, refreshing courses...");
          fetchCourses();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(subscription);
    };
  }, [user]);

  const handleGoalCreated = () => {
    console.log("Goal created, refreshing courses...");
    fetchCourses();
    setShowCreateGoal(false);
  };

  const handleUploadComplete = () => {
    setShowQuizGenerationDialog(true);
  };

  // ✅ FIXED: Implemented continue learning functionality
  const handleContinueLearning = async (courseTitle: string) => {
    if (!user) {
      toast({
        title: "Authentication Required",
        description: "Please log in to continue learning.",
        variant: "destructive",
      });
      return;
    }

    try {
      setIsContinuing(true);
      
      // Get the course data to find the lesson ID
      const course = courses.find(c => c.title === courseTitle);
      if (!course) {
        throw new Error("Course not found");
      }

      // Get learning plan status to find the current lesson
      let planStatus = null;
      let lessonId = null;
      
      try {
        planStatus = await agentService.getLearningPlanStatus(user.id);
        
        // Find the next lesson to continue with
        if (planStatus && planStatus.curriculum) {
          // Find the first incomplete lesson
          const incompleteLesson = planStatus.curriculum.find((lesson: any) => 
            !lesson.completed && lesson.progress < 100
          );
          lessonId = incompleteLesson?.id || planStatus.curriculum[0]?.id;
        }
      } catch (error) {
        console.log("No existing learning plan found, creating new session");
        // If no learning plan exists, we'll create a new session
      }

      // Create session request with appropriate lesson ID
      const sessionRequest = {
        user_id: user.id,
        lesson_id: lessonId || `lesson_${courseTitle.toLowerCase().replace(/\s+/g, '_')}`,
        session_preferences: {
          course_name: courseTitle,
          subject: course.subject,
          difficulty: "medium",
          learning_style: "adaptive"
        }
      };

      const sessionResponse = await agentService.startLearningSession(sessionRequest);
      
      // Navigate to chat view with the session
      setCurrentSessionId(sessionResponse.session_id);
      setCurrentCourseName(courseTitle);
      setView("chat");
      
      const sessionType = lessonId ? "Resumed" : "Started";
      toast({
        title: `Learning Session ${sessionType}`,
        description: `Continuing ${courseTitle} - Session ID: ${sessionResponse.session_id}`,
      });

    } catch (error: any) {
      console.error("Error continuing learning:", error);
      toast({
        title: "Error Starting Session",
        description: error.message || "Failed to start learning session. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsContinuing(false);
    }
  };

  // Navigation handlers
  if (view === "chat") {
    return (
      <ChatView
        documentId={latestDoc?.id}
        onBack={() => {
          setView("dashboard");
          setCurrentSessionId(null);
          setCurrentCourseName(null);
        }}
        sessionId={currentSessionId}
        courseName={currentCourseName}
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
      
      {/* Welcome Header */}
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

      {/* Quick Stats */}
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
        {/* Active Courses */}
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

                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full mt-2 bg-card text-foreground border border-border hover:bg-gradient-to-r hover:from-blue-500 hover:to-purple-500 transition-all duration-300"
                      onClick={() => handleContinueLearning(course.title)}
                      disabled={isContinuing}
                    >
                      {isContinuing ? "Starting Session..." : `Continue ${course.title}`}
                    </Button>
                  </motion.div>
                ))
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Today's Tasks and Quick Actions */}
        <div className="space-y-6">
          {/* Today's Tasks */}
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

  function handleQuickAction(action: string) {
    console.log(`Quick action: ${action}`);
    // Implement your action handlers here
  }

  function handleGoToAiChat() {
    console.log("Navigating to AI Chat");
    // Implement navigation logic here
  }
};