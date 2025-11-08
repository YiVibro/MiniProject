import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  CheckCircle2, 
  XCircle, 
  AlertTriangle,
  BookOpen,
  Target,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { EvaluateAssessmentResponse } from '@/lib/agentService';
import confetti from 'canvas-confetti';

interface GapAnalysisPanelProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  results: EvaluateAssessmentResponse | null;
  onContinue: () => void;
}

export const GapAnalysisPanel: React.FC<GapAnalysisPanelProps> = ({
  open,
  onOpenChange,
  results,
  onContinue
}) => {
  React.useEffect(() => {
    if (open && results?.passed) {
      // Trigger confetti for passed assessment
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
      });
    }
  }, [open, results]);

  if (!results) return null;

  const scorePercentage = results.score * 100;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {results.passed ? (
              <>
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                Assessment Passed! 🎉
              </>
            ) : (
              <>
                <XCircle className="h-5 w-5 text-orange-500" />
                Assessment Results
              </>
            )}
          </DialogTitle>
          <DialogDescription>
            {results.passed 
              ? 'Congratulations! You have successfully demonstrated your understanding.'
              : 'Here are areas where you can improve your understanding.'
            }
          </DialogDescription>
        </DialogHeader>

        {/* Score Overview */}
        <Card className={results.passed ? 'border-green-200' : 'border-orange-200'}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold">Your Score</h3>
                <p className="text-muted-foreground">
                  {results.passed ? 'You passed the assessment!' : 'Review recommended before continuing'}
                </p>
              </div>
              <div className="text-right">
                <div className={`text-3xl font-bold ${
                  results.passed ? 'text-green-600' : 'text-orange-600'
                }`}>
                  {scorePercentage.toFixed(1)}%
                </div>
                <div className="text-sm text-muted-foreground">
                  Passing: 70%
                </div>
              </div>
            </div>
            <Progress 
              value={scorePercentage} 
              className={`w-full h-3 ${
                results.passed ? '[&>div]:bg-green-500' : '[&>div]:bg-orange-500'
              }`}
            />
          </CardContent>
        </Card>

        {/* Gap Analysis */}
        {results.gaps.length > 0 && (
          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-500" />
                Learning Gaps Identified
              </h3>
              <div className="space-y-3">
                {results.gaps.map((gap, index) => (
                  <div key={index} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{gap.concept}</span>
                      <Badge 
                        variant={
                          gap.severity === 'high' ? 'destructive' :
                          gap.severity === 'medium' ? 'default' : 'secondary'
                        }
                      >
                        {gap.severity} priority
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{gap.description}</p>
                    <div className="text-sm">
                      <strong>Suggestions:</strong>
                      <ul className="list-disc list-inside mt-1 space-y-1">
                        {gap.remedial_suggestions.map((suggestion, i) => (
                          <li key={i}>{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Remedial Content */}
        {results.remedial_content && (
          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                Recommended Review
              </h3>
              <div className="space-y-3">
                <h4 className="font-medium">{results.remedial_content.title}</h4>
                <p className="text-sm text-muted-foreground">
                  {results.remedial_content.content}
                </p>
                {results.remedial_content.resources.length > 0 && (
                  <div>
                    <strong className="text-sm">Additional Resources:</strong>
                    <ul className="list-disc list-inside mt-1 space-y-1 text-sm text-muted-foreground">
                      {results.remedial_content.resources.map((resource, i) => (
                        <li key={i}>{resource}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Next Steps */}
        {results.next_steps.length > 0 && (
          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Target className="h-5 w-5" />
                Recommended Next Steps
              </h3>
              <div className="space-y-2">
                {results.next_steps.map((step, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    {step}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end gap-2">
          {!results.passed && (
            <Button variant="outline" onClick={onContinue}>
              Review Material
            </Button>
          )}
          <Button onClick={onContinue} className="gap-2">
            {results.passed ? (
              <>
                <Sparkles className="h-4 w-4" />
                Continue Learning
              </>
            ) : (
              <>
                <BookOpen className="h-4 w-4" />
                Try Again
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};