import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, ArrowRight, BookOpen } from 'lucide-react';

interface LessonContentViewProps {
  lesson: any;
  onComplete: () => void;
  onTakeQuiz: () => void;
}

export const LessonContentView: React.FC<LessonContentViewProps> = ({
  lesson,
  onComplete,
  onTakeQuiz
}) => {
  return (
    <div className="space-y-6">
      {/* Lesson Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>{lesson.title}</span>
            <div className="flex gap-2">
              <Badge>{lesson.difficulty}</Badge>
              <Badge variant="outline">{lesson.duration} min</Badge>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Learning Objectives */}
      {lesson.metadata?.learning_objectives && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Learning Objectives
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {lesson.metadata.learning_objectives.map((obj: string, i: number) => (
                <li key={i} className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>{obj}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* ✅ MAIN LESSON CONTENT */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Lesson Content</CardTitle>
        </CardHeader>
        <CardContent>
          <div 
            className="prose max-w-none dark:prose-invert"
            dangerouslySetInnerHTML={{ __html: lesson.metadata?.content || lesson.content }}
          />
        </CardContent>
      </Card>

      {/* ✅ SUBTOPICS */}
      {lesson.metadata?.subtopics && lesson.metadata.subtopics.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Topics Covered</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3">
              {lesson.metadata.subtopics.map((subtopic: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between p-3 border rounded-lg">
                  <span className="font-medium">{subtopic.title}</span>
                  <Badge variant="outline">{subtopic.deadline_minutes} min</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        <Button onClick={onComplete} className="flex-1 gap-2">
          <CheckCircle2 className="h-4 w-4" />
          Complete Lesson
        </Button>
        
        {lesson.metadata?.questions && lesson.metadata.questions.length > 0 && (
          <Button onClick={onTakeQuiz} variant="outline" className="flex-1 gap-2">
            Take Quiz ({lesson.metadata.questions.length} questions)
            <ArrowRight className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
};