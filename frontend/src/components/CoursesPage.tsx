import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";
import { useAuth } from "../store/AuthContext";
import { supabase } from "../lib/supabaseClient";
import { PDFContent } from "./PDFContent";
import { ActionButtons } from "./ActionButtons";
import { RecentUploads } from "./RecentUploads";
import { CreateGoalDialog } from "./CreateGoalDialog";
import { QuizGenerationDialog } from "./QuizGenerationDialog";

export const CoursesPage = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [latestDoc, setLatestDoc] = useState<{ id: number } | null>(null);
  const [view, setView] = useState<"document" | "chat" | "quiz">("document");
  const [currentQuizId, setCurrentQuizId] = useState<number | null>(null);
  const [showQuizGenerationDialog, setShowQuizGenerationDialog] = useState(false);
  const [showCreateGoal, setShowCreateGoal] = useState(false);

  // ✅ FIXED: Properly defined fetchCourses with category join
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

      console.log("CoursesPage - Fetched courses:", data); // Debug log

      const formattedCourses = data.map((course: any) => ({
        id: course.id,
        title: course.course_name,
        subject: course.categories?.name || `Category ${course.category_id?.slice(0, 4) || 'General'}`,
        progress: course.progress_percent || 0,
        description: `Continue your learning journey`,
        totalLessons: 10,
        completedLessons: Math.round(((course.progress_percent || 0) / 100) * 10),
      }));

      setCourses(formattedCourses);
    } catch (error: any) {
      console.error("Error fetching courses:", error.message);
    } finally {
      setLoading(false);
    }
  };

  // ✅ FIXED: Added real-time subscription
  useEffect(() => {
    if (!user) return;

    fetchCourses();

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
          console.log("CoursesPage - Real-time update received");
          fetchCourses();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(subscription);
    };
  }, [user]);

  // ✅ FIXED: Added missing fetchLatestDocument function
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
      fetchLatestDocument();
    }
  }, [user]);

  if (loading) {
    return (
      <div className="p-6 space-y-6 bg-background text-foreground min-h-screen transition-colors duration-500">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <BookOpen className="w-8 h-8 text-primary dark:text-primary/80" />
              My Courses
            </h1>
            <p className="text-muted-foreground dark:text-muted-foreground/70">
              Loading your courses...
            </p>
          </div>
        </div>
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-background text-foreground min-h-screen transition-colors duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BookOpen className="w-8 h-8 text-primary dark:text-primary/80" />
            My Courses
          </h1>
          <p className="text-muted-foreground dark:text-muted-foreground/70">
            Track your learning progress and continue your studies
          </p>
        </div>
        <div className="text-sm text-muted-foreground">
          {courses.length} course{courses.length !== 1 ? "s" : ""} enrolled
        </div>
      </div>

      {/* Courses Grid */}
      {courses.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No courses yet</h3>
          <p className="text-muted-foreground mb-6">
            Start by creating your first learning goal to see courses here.
          </p>
          <Button
            onClick={() => setShowCreateGoal(true)}
            className="gap-2 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-purple-500 hover:to-blue-500 text-white"
          >
            <Plus className="w-4 h-4" />
            Create Your First Goal
          </Button>
        </div>
      ) : (
        <motion.div
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
          initial="hidden"
          animate="visible"
          variants={{
            hidden: {},
            visible: { transition: { staggerChildren: 0.1 } },
          }}
        >
          {courses.map((course, index) => (
            <motion.div
              key={course.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1, duration: 0.4 }}
              whileHover={{ scale: 1.03 }}
            >
              <Card className="hover:shadow-lg transition-shadow h-full flex flex-col bg-card border border-border dark:bg-card/80 dark:border-border/50">
                <CardHeader>
                  <CardTitle className="text-foreground dark:text-foreground/90">
                    {course.title}
                  </CardTitle>
                  <div className="flex items-center justify-between">
                    <motion.span
                      className="text-sm text-muted-foreground dark:text-muted-foreground/70"
                      whileHover={{ opacity: 1 }}
                    >
                      {course.subject}
                    </motion.span>
                    <div className="flex items-center gap-1 text-sm text-primary dark:text-primary/80">
                      <TrendingUp className="w-4 h-4" />
                      {course.progress}%
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4 flex flex-col justify-between flex-1">
                  <p className="text-sm text-muted-foreground dark:text-muted-foreground/70">
                    {course.description}
                  </p>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm text-foreground dark:text-foreground/80">
                      <span>Progress</span>
                      <span>
                        {course.completedLessons}/{course.totalLessons} lessons
                      </span>
                    </div>
                    <motion.div
                      className="w-full bg-muted dark:bg-muted/30 rounded-full h-2 overflow-hidden"
                      initial={{ width: 0 }}
                      animate={{ width: "100%" }}
                      transition={{ duration: 0.8 }}
                    >
                      <motion.div
                        className="bg-primary dark:bg-primary/80 h-2 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${course.progress}%` }}
                        transition={{ duration: 1.2, ease: "easeInOut" }}
                      />
                    </motion.div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* PDF + Actions Section */}
      <div className="p-6 space-y-6">
        {latestDoc && (
          <div className="space-y-6">
            <PDFContent documentId={latestDoc.id} />
            <ActionButtons
              onChat={() => setView("chat")}
              onQuiz={() => setShowQuizGenerationDialog(true)}
            />
          </div>
        )}
        <RecentUploads onSelect={(id) => setLatestDoc({ id })} />
      </div>

      {/* Dialogs */}
      <CreateGoalDialog
        open={showCreateGoal}
        onOpenChange={setShowCreateGoal}
        onGoalCreated={() => fetchCourses()}
      />

      <QuizGenerationDialog
        open={showQuizGenerationDialog}
        onOpenChange={setShowQuizGenerationDialog}
        documentId={latestDoc?.id}
        onGenerate={(options) => {
          fetch("http://127.0.0.1:8000/api/quiz/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              document_id: latestDoc?.id,
              num_questions: options.num_questions,
              question_types: options.question_types,
              difficulty: options.difficulty,
              focus_topics: ["general"],
            }),
          })
            .then((res) => {
              if (!res.ok) {
                return res.json().then((errorBody) => {
                  throw new Error(
                    `Quiz generation failed with status ${res.status}: ${JSON.stringify(errorBody)}`
                  );
                });
              }
              return res.json();
            })
            .then((data) => {
              console.log("Quiz generated:", data);
              const generatedQuizId = data?.quiz?.id ?? data?.id;
              if (generatedQuizId) {
                setCurrentQuizId(generatedQuizId);
                setShowQuizGenerationDialog(false);
                setView("quiz");
              } else {
                throw new Error("Quiz generation response missing quiz id");
              }
            })
            .catch((err) => console.error("Quiz generation failed:", err));
        }}
      />
    </div>
  );
};

// ✅ FIXED: Added missing imports
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";