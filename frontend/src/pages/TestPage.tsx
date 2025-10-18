import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface MCQOption {
  text: string;
  correct?: boolean;
}

interface Question {
  id: string;
  question: string;
  type: "multiple_choice" | "short_answer";
  options?: MCQOption[];
}

const TestPage = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const location = useLocation() as any;
  const incomingQuestions: Question[] | undefined = location?.state?.questions;

  // Get course-specific dummy questions if none were provided
  const getCourseSpecificQuestions = (courseId: string): Question[] => {
    const courseQuestions: { [key: string]: Question[] } = {
      "1": [ // Advanced Mathematics
        {
          id: "math-test-1",
          question: "What is the derivative of sin(x)?",
          type: "multiple_choice",
          options: [
            { text: "cos(x)", correct: true },
            { text: "-cos(x)", correct: false },
            { text: "sin(x)", correct: false },
            { text: "-sin(x)", correct: false }
          ],
        },
        {
          id: "math-test-2",
          question: "What is the integral of 1/x?",
          type: "multiple_choice",
          options: [
            { text: "ln|x| + C", correct: true },
            { text: "x + C", correct: false },
            { text: "1/x² + C", correct: false },
            { text: "x² + C", correct: false }
          ],
        },
        {
          id: "math-test-3",
          question: "What is the limit of (sin x)/x as x approaches 0?",
          type: "multiple_choice",
          options: [
            { text: "1", correct: true },
            { text: "0", correct: false },
            { text: "∞", correct: false },
            { text: "undefined", correct: false }
          ],
        },
        {
          id: "math-test-4",
          question: "What is the derivative of e^x?",
          type: "multiple_choice",
          options: [
            { text: "e^x", correct: true },
            { text: "xe^x", correct: false },
            { text: "ln(x)", correct: false },
            { text: "1/x", correct: false }
          ],
        },
        {
          id: "math-test-5",
          question: "What is the integral of x²?",
          type: "multiple_choice",
          options: [
            { text: "x³/3 + C", correct: true },
            { text: "x³ + C", correct: false },
            { text: "2x + C", correct: false },
            { text: "x²/2 + C", correct: false }
          ],
        },
        {
          id: "math-test-6",
          question: "What is the chain rule used for?",
          type: "multiple_choice",
          options: [
            { text: "Finding derivatives of composite functions", correct: true },
            { text: "Finding integrals", correct: false },
            { text: "Finding limits", correct: false },
            { text: "Finding antiderivatives", correct: false }
          ],
        },
        {
          id: "math-test-7",
          question: "Explain the fundamental theorem of calculus and its significance",
          type: "short_answer",
        },
        {
          id: "math-test-8",
          question: "What is the derivative of ln(x)?",
          type: "multiple_choice",
          options: [
            { text: "1/x", correct: true },
            { text: "x", correct: false },
            { text: "e^x", correct: false },
            { text: "1/e^x", correct: false }
          ],
        },
        {
          id: "math-test-9",
          question: "What is the integral of cos(x)?",
          type: "multiple_choice",
          options: [
            { text: "sin(x) + C", correct: true },
            { text: "-sin(x) + C", correct: false },
            { text: "cos(x) + C", correct: false },
            { text: "-cos(x) + C", correct: false }
          ],
        },
        {
          id: "math-test-10",
          question: "Describe the relationship between derivatives and integrals in calculus",
          type: "short_answer",
        }
      ],
      "2": [ // Physics Fundamentals
        {
          id: "physics-test-1",
          question: "What is the speed of light in vacuum?",
          type: "multiple_choice",
          options: [
            { text: "3 × 10⁸ m/s", correct: true },
            { text: "3 × 10⁶ m/s", correct: false },
            { text: "3 × 10⁹ m/s", correct: false },
            { text: "3 × 10⁷ m/s", correct: false }
          ],
        },
        {
          id: "physics-test-2",
          question: "What is the formula for gravitational potential energy?",
          type: "multiple_choice",
          options: [
            { text: "PE = mgh", correct: true },
            { text: "PE = ½mv²", correct: false },
            { text: "PE = Fd", correct: false },
            { text: "PE = ma", correct: false }
          ],
        },
        {
          id: "physics-test-3",
          question: "What is the unit of force in the SI system?",
          type: "multiple_choice",
          options: [
            { text: "Newton (N)", correct: true },
            { text: "Joule (J)", correct: false },
            { text: "Watt (W)", correct: false },
            { text: "Pascal (Pa)", correct: false }
          ],
        },
        {
          id: "physics-test-4",
          question: "What is Newton's Second Law of Motion?",
          type: "multiple_choice",
          options: [
            { text: "F = ma", correct: true },
            { text: "F = mv", correct: false },
            { text: "F = mgh", correct: false },
            { text: "F = ½mv²", correct: false }
          ],
        },
        {
          id: "physics-test-5",
          question: "What is the acceleration due to gravity on Earth?",
          type: "multiple_choice",
          options: [
            { text: "9.8 m/s²", correct: true },
            { text: "10 m/s²", correct: false },
            { text: "9.8 m/s", correct: false },
            { text: "32 ft/s²", correct: false }
          ],
        },
        {
          id: "physics-test-6",
          question: "What is the formula for kinetic energy?",
          type: "multiple_choice",
          options: [
            { text: "KE = ½mv²", correct: true },
            { text: "KE = mv", correct: false },
            { text: "KE = mgh", correct: false },
            { text: "KE = ½mv", correct: false }
          ],
        },
        {
          id: "physics-test-7",
          question: "What is the law of conservation of energy?",
          type: "multiple_choice",
          options: [
            { text: "Energy cannot be created or destroyed", correct: true },
            { text: "Energy can be created but not destroyed", correct: false },
            { text: "Energy can be destroyed but not created", correct: false },
            { text: "Energy is always increasing", correct: false }
          ],
        },
        {
          id: "physics-test-8",
          question: "What is the unit of power?",
          type: "multiple_choice",
          options: [
            { text: "Watt (W)", correct: true },
            { text: "Joule (J)", correct: false },
            { text: "Newton (N)", correct: false },
            { text: "Pascal (Pa)", correct: false }
          ],
        },
        {
          id: "physics-test-9",
          question: "Explain the difference between speed and velocity",
          type: "short_answer",
        },
        {
          id: "physics-test-10",
          question: "What is the relationship between frequency and wavelength?",
          type: "multiple_choice",
          options: [
            { text: "c = fλ", correct: true },
            { text: "c = f/λ", correct: false },
            { text: "c = f + λ", correct: false },
            { text: "c = f - λ", correct: false }
          ],
        }
      ],
      "3": [ // Chemistry Review
        {
          id: "chem-test-1",
          question: "What is Avogadro's number?",
          type: "multiple_choice",
          options: [
            { text: "6.022 × 10²³", correct: true },
            { text: "6.022 × 10²²", correct: false },
            { text: "6.022 × 10²⁴", correct: false },
            { text: "6.022 × 10²¹", correct: false }
          ],
        },
        {
          id: "chem-test-2",
          question: "What is the pH of a neutral solution?",
          type: "multiple_choice",
          options: [
            { text: "7", correct: true },
            { text: "0", correct: false },
            { text: "14", correct: false },
            { text: "1", correct: false }
          ],
        },
        {
          id: "chem-test-3",
          question: "What is the molecular formula of water?",
          type: "multiple_choice",
          options: [
            { text: "H₂O", correct: true },
            { text: "H₂O₂", correct: false },
            { text: "HO", correct: false },
            { text: "H₃O", correct: false }
          ],
        },
        {
          id: "chem-test-4",
          question: "What is the atomic number of carbon?",
          type: "multiple_choice",
          options: [
            { text: "6", correct: true },
            { text: "12", correct: false },
            { text: "8", correct: false },
            { text: "14", correct: false }
          ],
        },
        {
          id: "chem-test-5",
          question: "What is the ideal gas law?",
          type: "multiple_choice",
          options: [
            { text: "PV = nRT", correct: true },
            { text: "PV = nR", correct: false },
            { text: "P = nRT", correct: false },
            { text: "V = nRT", correct: false }
          ],
        },
        {
          id: "chem-test-6",
          question: "What type of bond forms between a metal and non-metal?",
          type: "multiple_choice",
          options: [
            { text: "Ionic bond", correct: true },
            { text: "Covalent bond", correct: false },
            { text: "Metallic bond", correct: false },
            { text: "Hydrogen bond", correct: false }
          ],
        },
        {
          id: "chem-test-7",
          question: "What is the general formula for alkanes?",
          type: "multiple_choice",
          options: [
            { text: "CnH2n+2", correct: true },
            { text: "CnH2n", correct: false },
            { text: "CnH2n-2", correct: false },
            { text: "CnHn", correct: false }
          ],
        },
        {
          id: "chem-test-8",
          question: "What functional group is present in alcohols?",
          type: "multiple_choice",
          options: [
            { text: "-OH", correct: true },
            { text: "-COOH", correct: false },
            { text: "-CHO", correct: false },
            { text: "-NH2", correct: false }
          ],
        },
        {
          id: "chem-test-9",
          question: "What is the rate law for a first-order reaction?",
          type: "multiple_choice",
          options: [
            { text: "Rate = k[A]", correct: true },
            { text: "Rate = k[A]²", correct: false },
            { text: "Rate = k", correct: false },
            { text: "Rate = k[A][B]", correct: false }
          ],
        },
        {
          id: "chem-test-10",
          question: "Explain the difference between ionic and covalent bonds",
          type: "short_answer",
        },
        {
          id: "chem-test-11",
          question: "What is the unit of concentration in molarity?",
          type: "multiple_choice",
          options: [
            { text: "mol/L", correct: true },
            { text: "mol/mL", correct: false },
            { text: "g/L", correct: false },
            { text: "mol/kg", correct: false }
          ],
        },
        {
          id: "chem-test-12",
          question: "Describe the periodic trends in atomic radius and explain why they occur",
          type: "short_answer",
        }
      ]
    };

    return courseQuestions[courseId] || [
      {
        id: "default-test-1",
        question: "What is the main topic of this course?",
        type: "short_answer",
      },
      {
        id: "default-test-2",
        question: "Explain one key concept you've learned",
        type: "short_answer",
      },
      {
        id: "default-test-3",
        question: "What would you like to learn more about?",
        type: "short_answer",
      }
    ];
  };

  // Use incoming questions or fallback to course-specific questions
  const questions = useMemo<Question[]>(() => {
    if (incomingQuestions && incomingQuestions.length > 0) {
      // Convert the incoming questions to the proper format
      return incomingQuestions.map((q: any) => ({
        id: q.id,
        question: q.question,
        type: q.type || "multiple_choice",
        options: q.options ? q.options.map((opt: any) => ({
          text: opt.text,
          correct: opt.correct || false
        })) : []
      }));
    }
    return getCourseSpecificQuestions(courseId || "default");
  }, [incomingQuestions, courseId]);

  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  const submit = async () => {
    setSubmitting(true);
    try {
      // Submit answers to backend when available; for now just confirm
      alert("Answers submitted. Great job!");
      navigate(`/course/${courseId}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Course Test</h1>
        <Button variant="outline" onClick={() => navigate(-1)}>Back</Button>
      </div>

      <div className="space-y-4">
        {questions.map((q) => (
          <Card key={q.id}>
            <CardHeader>
              <CardTitle className="text-base">{q.question}</CardTitle>
            </CardHeader>
            <CardContent>
              {q.type === "multiple_choice" && (
                <RadioGroup
                  value={answers[q.id] || ""}
                  onValueChange={(v) => setAnswers((prev) => ({ ...prev, [q.id]: v }))}
                >
                  {(q.options || []).map((opt, idx) => {
                    const value = `${idx}`;
                    const rid = `${q.id}-${idx}`;
                    return (
                      <div key={rid} className="flex items-center space-x-2 py-1">
                        <RadioGroupItem id={rid} value={value} />
                        <Label htmlFor={rid}>{opt.text}</Label>
                      </div>
                    );
                  })}
                </RadioGroup>
              )}
              {q.type === "short_answer" && (
                <Textarea
                  placeholder="Type your answer here..."
                  value={answers[q.id] || ""}
                  onChange={(e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
                  className="min-h-32"
                />
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="flex justify-end">
        <Button onClick={submit} disabled={submitting}>{submitting ? "Submitting..." : "Submit"}</Button>
      </div>
    </div>
  );
};

export default TestPage;



