// QuizGenerationDialog.tsx
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";

interface QuizGenerationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  documentId: number;
  onGenerate: (options: {
    document_id: number;
    num_questions: number;
    question_types: string[];
    difficulty: string;
  }) => void;
}

export const QuizGenerationDialog = ({ open, onOpenChange, onGenerate,documentId }: QuizGenerationDialogProps) => {
  const [numQuestions, setNumQuestions] = useState(5);
  const [questionType, setQuestionType] = useState("mcq");
  const [difficulty, setDifficulty] = useState("medium");

  const handleSubmit = () => {
    // FIX: Map local state to the snake_case payload expected by the API endpoint, 
    // wrapping the single questionType into a question_types array.
    onGenerate({
      document_id: documentId,
      num_questions: numQuestions,
      question_types: [questionType],
      difficulty
    });
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Generate Quiz</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label>Number of Questions</Label>
            <Input
              type="number"
              value={numQuestions}
              onChange={(e) => setNumQuestions(Number(e.target.value))}
            />
          </div>

          <div>
            <Label>Question Type</Label>
            <Select value={questionType} onValueChange={setQuestionType}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="mcq">MCQ</SelectItem>
                <SelectItem value="fill_blank">Fill in the Blank</SelectItem>
                <SelectItem value="true_false">True/False</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Difficulty</Label>
            <Select value={difficulty} onValueChange={setDifficulty}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="easy">Easy</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="hard">Hard</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <Button onClick={handleSubmit} className="mt-4 w-full">Generate Quiz</Button>
      </DialogContent>
    </Dialog>
  );
};