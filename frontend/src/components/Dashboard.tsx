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

export const Dashboard = () => {
  const [showCreateGoal, setShowCreateGoal] = useState(false);
  const { user } = useAuth();
  const [courses, setCourses] = useState<any[]>([]);

  useEffect(() => {
    if (user) {
      fetchCourses();
    }
  }, [user]);

  const fetchCourses = async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from('user_progress')
        .select(`
          id,
          course_name,
          progress_percent,
          categories (name)
        `)
        .eq('user_id', user.id);

      if (error) throw error;

      const formattedCourses = data.map((course: any) => ({
        id: course.id,
        title: course.course_name,
        subject: course.categories.name,
        progress: course.progress_percent,
        goalType: "new learning",
        dueDate: "N/A",
        totalLessons: 10,
        completedLessons: Math.round((course.progress_percent / 100) * 10),
      }));

      setCourses(formattedCourses);
    } catch (error: any) {
      console.error("Error fetching courses:", error.message);
    }
  };

  const handleGoToAiChat = () => {
    // Navigate to AI chat - implement your navigation logic here
    console.log("Navigating to AI Chat");
    // Example: navigate('/ai-chat') if using react-router
  };

  const handleContinueLearning = (courseTitle: string) => {
    // Navigate to course - implement your navigation logic here
    console.log(`Continuing course: ${courseTitle}`);
    // Example: navigate(`/course/${courseId}`)
  };

  const handleQuickAction = (action: string) => {
    console.log(`Quick action: ${action}`);
    // Implement your action handlers here
  };

    const handleGoalCreated = () => {
    // Refresh courses after a new goal is created
    fetchCourses();
    setShowCreateGoal(false);
  };

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
          <h1 className="text-3xl font-bold">Welcome back, {user?.user_metadata.full_name || 'Student'}!</h1>
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
          { icon: TrendingUp, label: "Avg Progress", value: "87%", color: "from-purple-500 to-purple-700" },
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
              </CardTitle>
              <CardDescription className="text-muted-foreground">
                Continue where you left off
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {courses.map((course, index) => (
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
                    onClick={() => alert(`Continuing course: ${course.title}`)} // Placeholder action
                  >
                    Continue Learning
                  </Button>
                </motion.div>
              ))}
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

          {/* Quick Actions */}
          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Card className={cardClasses}>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {[
                  { icon: Brain, label: "Ask AI Tutor", action: (handleGoToAiChat) },
                  { icon: BookOpen, label: "Take Practice Test", action: () => handleQuickAction("practice-test") },
                  { icon: TrendingUp, label: "View Progress", action: () => handleQuickAction("view-progress") },
                ].map((action, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    size="sm"
                    className="w-full justify-start gap-2 bg-card text-foreground border border-border hover:bg-gradient-to-r hover:from-blue-500 hover:to-purple-500 hover:text-white transition-all duration-300"
                    onClick={action.action}
                  >
                    <action.icon className="w-4 h-4" />
                    {action.label}
                  </Button>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>

      <CreateGoalDialog open={showCreateGoal} onOpenChange={setShowCreateGoal} onGoalCreated={handleGoalCreated} />
    </div>
  );
};