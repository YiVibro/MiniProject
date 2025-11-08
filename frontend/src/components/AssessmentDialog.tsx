import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Clock, 
  CheckCircle2, 
  XCircle,
  ArrowRight,
  AlertCircle
} from 'lucide-react';
import { AssessmentResponse } from '@/lib/agentService';

interface AssessmentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  assessment: AssessmentResponse | null;
  onSubmit: (answers: Record<string, any>) => void;
  isSubmitting: boolean;
}

export const AssessmentDialog: React.FC<AssessmentDialogProps> = ({
  open,
  onOpenChange,
  assessment,
  onSubmit,
  isSubmitting
}) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [timeLeft, setTimeLeft] = useState(assessment?.time_limit ? assessment.time_limit * 60 : 1800);

  React.useEffect(() => {
    if (!open) {
      setCurrentQuestion(0);
      setAnswers({});
      setTimeLeft(assessment?.time_limit ? assessment.time_limit * 60 : 1800);
    }
  }, [open, assessment]);

  React.useEffect(() => {
    if (!open || !assessment) return;

    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [open, assessment]);

  const handleAnswerChange = (questionId: string, answer: any) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleNext = () => {
    if (assessment && currentQuestion < assessment.questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleSubmit = () => {
    onSubmit(answers);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!assessment) return null;

  const question = assessment.questions[currentQuestion];
  const progress = ((currentQuestion + 1) / assessment.questions.length) * 100;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            Knowledge Check
          </DialogTitle>
          <DialogDescription>
            Complete this assessment to demonstrate your understanding of the lesson.
          </DialogDescription>
        </DialogHeader>

        {/* Progress and Timer */}
        <div className="space-y-4">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-4">
              <Badge variant="outline">
                Question {currentQuestion + 1} of {assessment.questions.length}
              </Badge>
              <div className="flex items-center gap-1 text-muted-foreground">
                <Clock className="h-4 w-4" />
                {formatTime(timeLeft)}
              </div>
            </div>
            <div className="text-muted-foreground">
              Passing: {(assessment.passing_score * 100).toFixed(0)}%
            </div>
          </div>
          <Progress value={progress} className="w-full" />
        </div>

        {/* Question */}
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">{question.question}</h3>
              
              {question.type === 'multiple_choice' && (
                <RadioGroup
                  value={answers[question.id] || ''}
                  onValueChange={(value) => handleAnswerChange(question.id, value)}
                >
                  {question.options?.map((option, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <RadioGroupItem value={option} id={`option-${index}`} />
                      <Label htmlFor={`option-${index}`}>{option}</Label>
                    </div>
                  ))}
                </RadioGroup>
              )}

              {question.type === 'true_false' && (
                <RadioGroup
                  value={answers[question.id] || ''}
                  onValueChange={(value) => handleAnswerChange(question.id, value)}
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="true" id="true" />
                    <Label htmlFor="true">True</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="false" id="false" />
                    <Label htmlFor="false">False</Label>
                  </div>
                </RadioGroup>
              )}

              {question.type === 'short_answer' && (
                <Textarea
                  value={answers[question.id] || ''}
                  onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                  placeholder="Type your answer here..."
                  rows={4}
                />
              )}
            </div>
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
          >
            Previous
          </Button>
          
          {currentQuestion < assessment.questions.length - 1 ? (
            <Button onClick={handleNext} className="gap-2">
              Next Question
              <ArrowRight className="h-4 w-4" />
            </Button>
          ) : (
            <Button 
              onClick={handleSubmit} 
              disabled={isSubmitting}
              className="gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current" />
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-4 w-4" />
                  Submit Assessment
                </>
              )}
            </Button>
          )}
        </div>

        {/* Question Navigation Dots */}
        <div className="flex justify-center gap-2">
          {assessment.questions.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentQuestion(index)}
              className={`w-3 h-3 rounded-full transition-colors ${
                index === currentQuestion
                  ? 'bg-primary'
                  : answers[assessment.questions[index].id]
                  ? 'bg-green-500'
                  : 'bg-muted'
              }`}
            />
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
};