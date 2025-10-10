import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import agentService from "@/lib/agentService";
import { useAuth } from "@/store/AuthContext";

interface TopicItem {
  id: string;
  title: string;
  difficulty: string;
  duration: number;
}

const CoursePage = () => {
  const { courseId } = useParams();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState<string>("Course");
  const [topics, setTopics] = useState<TopicItem[]>([]);

  useEffect(() => {
    const load = async () => {
      if (!courseId || !user) return;
      setLoading(true);
      setError(null);
      try {
        // There is no explicit get-course endpoint; we can infer topics from learning plan status
        const status = await agentService.getLearningPlanStatus(user.id);
        const plan = status?.plans?.[courseId] || status;
        const curriculum = plan?.curriculum || [];
        setTitle(plan?.learning_path?.title || plan?.title || "Course");
        setTopics(
          curriculum.map((c: any) => ({
            id: c.id,
            title: c.title,
            difficulty: c.difficulty,
            duration: c.duration,
          }))
        );
      } catch (e: any) {
        setError(e?.message || "Failed to load course");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [courseId, user]);

  const startLesson = async (lessonId: string) => {
    if (!user) return;
    const session = await agentService.startLearningSession({ user_id: user.id, lesson_id: lessonId });
    // In future we can show adaptive content; for now just alert to confirm backend connection
    alert(`Session started: ${session.session_id}`);
  };

  const takeTest = () => {
    alert("Test feature coming soon.");
  };

  const askAI = () => {
    window.open("/ai-chat", "_blank");
  };

  const openNotes = () => {
    window.open("/notes", "_blank");
  };

  if (loading) return <div className="p-6">Loading...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">{title}</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={askAI}>Ask AI</Button>
          <Button variant="outline" onClick={takeTest}>Take Test</Button>
          <Button variant="outline" onClick={openNotes}>Take Notes</Button>
        </div>
      </div>
      <Separator />

      <Card>
        <CardHeader>
          <CardTitle>Topics Covered</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {topics.length === 0 && (
              <div className="text-sm text-muted-foreground">No topics yet.</div>
            )}
            {topics.map((t) => (
              <div key={t.id} className="flex items-center justify-between border rounded-lg p-3">
                <div>
                  <div className="font-medium">{t.title}</div>
                  <div className="text-xs text-muted-foreground">Duration: {t.duration} mins</div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">{t.difficulty}</Badge>
                  <Button size="sm" onClick={() => startLesson(t.id)}>Start</Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="ai">
        <TabsList>
          <TabsTrigger value="ai">Ask AI</TabsTrigger>
          <TabsTrigger value="test">Take Test</TabsTrigger>
          <TabsTrigger value="notes">Take Notes</TabsTrigger>
        </TabsList>
        <TabsContent value="ai">
          <div className="text-sm text-muted-foreground">Open AI chat in a new tab to ask questions.</div>
        </TabsContent>
        <TabsContent value="test">
          <div className="text-sm text-muted-foreground">Start practice tests tailored to this course.</div>
        </TabsContent>
        <TabsContent value="notes">
          <div className="text-sm text-muted-foreground">Open notes to capture your learnings.</div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CoursePage;



