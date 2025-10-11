// QuizView.tsx
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

interface QuizViewProps {
  quizId: number;
  onBack?: () => void;
}

interface Question {
  id: number;
  question_text: string;
  question_type: string;
  options?: string[];
}

interface QuizData {
  id: number;
  title: string;
  questions: Question[];
}

interface Result {
  question_id: number;
  question_text: string;
  user_answer: string;
  is_correct: boolean;
  correct_answer: string;
  explanation?: string;
}

export const QuizView = ({ quizId, onBack }: QuizViewProps) => {
  const [quizData, setQuizData] = useState<QuizData | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<{ [key: number]: string }>({});
  const [results, setResults] = useState<Result[] | null>(null);

  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/api/quiz/quiz/${quizId}`);
        const data = await res.json();
        setQuizData(data);
      } catch (err) {
        console.error("Error fetching quiz:", err);
      }
    };

    if (quizId) {
      fetchQuiz();
    }
  }, [quizId]);

  const handleAnswer = (answer: string) => {
    if (quizData) {
      setAnswers({ ...answers, [quizData.questions[currentIndex].id]: answer });
    }
  };

  const nextQuestion = () => {
    if (quizData && currentIndex + 1 < quizData.questions.length) {
      setCurrentIndex(currentIndex + 1);
    } else {
      submitQuiz();
    }
  };

  const submitQuiz = async () => {
    if (!quizData) return;

    const submission = {
      answers: Object.entries(answers).map(([question_id, answer]) => ({
        question_id: parseInt(question_id),
        answer,
      })),
    };

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/quiz/quiz/${quizId}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(submission),
      });
      const resultData = await res.json();
      setResults(resultData.results);
    } catch (err) {
      console.error("Error submitting quiz:", err);
    }
  };

  if (!quizData) return <p>Loading quiz...</p>;

  if (results) {
    const score = results.filter((r) => r.is_correct).length;
    return (
      <Card>
        <CardHeader>
          <CardTitle>Quiz Results</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="font-bold mb-4">Score: {score} / {quizData.questions.length}</p>
          {results.map((r) => (
            <div key={r.question_id} className="mb-4 p-3 border rounded">
              <p className="font-semibold">{r.question_text}</p>
              <p>Your Answer: {r.user_answer} {r.is_correct ? "✅" : "❌"}</p>
              {!r.is_correct && <p>Correct Answer: {r.correct_answer}</p>}
              {r.explanation && <p className="text-sm text-muted-foreground">Explanation: {r.explanation}</p>}
            </div>
          ))}
          {onBack && <Button onClick={onBack}>⬅ Back</Button>}
        </CardContent>
      </Card>
    );
  }
  
  const currentQ = quizData.questions[currentIndex];
  if (!currentQ) return <p>Loading question...</p>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          Question {currentIndex + 1} / {quizData.questions.length}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="mb-4">{currentQ.question_text}</p>

        {currentQ.question_type === "mcq" && currentQ.options && (
          <div className="space-y-2">
            {currentQ.options.map((opt, i) => (
              <Button
                key={i}
                variant={answers[currentQ.id] === opt ? "default" : "outline"}
                onClick={() => handleAnswer(opt)}
                className="w-full"
              >
                {opt}
              </Button>
            ))}
          </div>
        )}

        {currentQ.question_type === "fill_blank" && (
          <input
            type="text"
            className="border p-2 w-full"
            value={answers[currentQ.id] || ""}
            onChange={(e) => handleAnswer(e.target.value)}
          />
        )}

        {currentQ.question_type === "true_false" && (
          <div className="space-y-2">
            <Button
              variant={answers[currentQ.id] === "True" ? "default" : "outline"}
              onClick={() => handleAnswer("True")}
              className="w-full"
            >
              True
            </Button>
            <Button
              variant={answers[currentQ.id] === "False" ? "default" : "outline"}
              onClick={() => handleAnswer("False")}
             className="w-full"
            >
              False
            </Button>
          </div>
        )}

        <Button className="mt-4 w-full" onClick={nextQuestion}>
          {currentIndex + 1 < quizData.questions.length ? "Next" : "Finish"}
        </Button>
      </CardContent>
    </Card>
  );
};
