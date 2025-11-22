import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, 
  CheckCircle2, 
  Lock, 
  PlayCircle,
  Target,
  BarChart3,
  ChevronDown,
  ChevronUp,
  FileText,
  HelpCircle,
  Clock
} from 'lucide-react';
import { LearningPathNode } from '@/lib/agentService';

interface LessonNodeProps {
  node: LearningPathNode;
  index: number;
  onStart: () => void;
  onComplete: () => void;
  isCurrent: boolean;
}

export const LessonNode: React.FC<LessonNodeProps> = ({
  node,
  index,
  onStart,
  onComplete,
  isCurrent
}) => {
  const [expanded, setExpanded] = useState(false);

  const getNodeIcon = () => {
    switch (node.type) {
      case 'lesson':
        return <BookOpen className="h-5 w-5" />;
      case 'practice':
        return <Target className="h-5 w-5" />;
      case 'assessment':
        return <BarChart3 className="h-5 w-5" />;
      case 'remedial':
        return <BookOpen className="h-5 w-5" />;
      default:
        return <BookOpen className="h-5 w-5" />;
    }
  };

  const getStatusIcon = () => {
    switch (node.status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'current':
        return <PlayCircle className="h-5 w-5 text-blue-500" />;
      case 'locked':
        return <Lock className="h-5 w-5 text-muted-foreground" />;
      default:
        return <div className="h-2 w-2 rounded-full bg-muted" />;
    }
  };

  const getNodeColor = () => {
    switch (node.status) {
      case 'completed':
        return 'border-green-200 bg-green-50 dark:bg-green-950/20 dark:border-green-800';
      case 'current':
        return 'border-blue-200 bg-blue-50 dark:bg-blue-950/20 dark:border-blue-800';
      case 'locked':
        return 'border-muted bg-muted/50';
      default:
        return 'border-border bg-card';
    }
  };

  // ✅ Count total questions from both questions and practice_exercises
  const totalQuestions = (node.metadata?.questions?.length || 0) + 
                        (node.metadata?.practice_exercises?.length || 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      <Card className={`relative overflow-hidden border-2 ${getNodeColor()} transition-all duration-300`}>
        {/* Connection line (except for last node) */}
        {index < 10 && ( // Assuming max 10 nodes for connection visualization
          <div className="absolute left-6 top-full h-6 w-0.5 bg-border z-0" />
        )}
        
        <CardContent className="p-4">
          <div className="flex items-start gap-4">
            {/* Node Icon */}
            <div className="flex-shrink-0">
              <div className={`p-2 rounded-full ${
                node.status === 'completed' ? 'bg-green-100 dark:bg-green-900' :
                node.status === 'current' ? 'bg-blue-100 dark:bg-blue-900' :
                'bg-muted'
              }`}>
                {getNodeIcon()}
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-lg">{node.title}</h3>
                {getStatusIcon()}
              </div>
              
              <p className="text-muted-foreground text-sm mb-2">{node.description}</p>
              
              <div className="flex items-center gap-2 mb-3">
                <Badge variant="outline" className="text-xs flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {node.duration} min
                </Badge>
                <Badge variant="secondary" className="text-xs capitalize">
                  {node.difficulty}
                </Badge>
                <Badge variant="outline" className="text-xs capitalize">
                  {node.type}
                </Badge>
                
                {/* ✅ ADD: Questions indicator */}
                {totalQuestions > 0 && (
                  <Badge variant="outline" className="text-xs flex items-center gap-1">
                    <HelpCircle className="h-3 w-3" />
                    {totalQuestions} Qs
                  </Badge>
                )}
              </div>

              {/* Prerequisites */}
              {node.prerequisites && node.prerequisites.length > 0 && (
                <div className="text-xs text-muted-foreground mb-3">
                  Requires: {node.prerequisites.join(', ')}
                </div>
              )}

              {/* ✅ ADD: Expandable subtopics section */}
              {node.metadata?.subtopics && node.metadata.subtopics.length > 0 && (
                <div className="mt-3 border-t pt-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setExpanded(!expanded)}
                    className="text-xs h-8 px-2"
                  >
                    {expanded ? (
                      <ChevronUp className="h-3 w-3 mr-1" />
                    ) : (
                      <ChevronDown className="h-3 w-3 mr-1" />
                    )}
                    {expanded ? 'Hide' : 'Show'} Subtopics ({node.metadata.subtopics.length})
                  </Button>
                  
                  {expanded && (
                    <motion.div 
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-2 space-y-2"
                    >
                      {node.metadata.subtopics.map((subtopic: any, idx: number) => (
                        <div 
                          key={idx} 
                          className="flex items-start gap-2 text-sm p-2 bg-muted/30 rounded-lg border"
                        >
                          <FileText className="h-3 w-3 text-muted-foreground mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-xs">{subtopic.title}</div>
                            {subtopic.content && (
                              <div className="text-muted-foreground text-xs mt-1">
                                {subtopic.content}
                              </div>
                            )}
                          </div>
                          <Badge variant="outline" className="text-[10px] flex items-center gap-1 flex-shrink-0">
                            <Clock className="h-2 w-2" />
                            {subtopic.duration_minutes || subtopic.deadline_minutes || 10}m
                          </Badge>
                        </div>
                      ))}
                    </motion.div>
                  )}
                </div>
              )}

              {/* ✅ ADD: Learning objectives preview */}
              {node.metadata?.learning_objectives && node.metadata.learning_objectives.length > 0 && (
                <div className="mt-2">
                  <div className="text-xs text-muted-foreground font-medium mb-1">
                    Learning Objectives:
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {node.metadata.learning_objectives.slice(0, 3).map((objective: string, idx: number) => (
                      <Badge key={idx} variant="outline" className="text-[10px]">
                        {objective.length > 30 ? objective.substring(0, 30) + '...' : objective}
                      </Badge>
                    ))}
                    {node.metadata.learning_objectives.length > 3 && (
                      <Badge variant="secondary" className="text-[10px]">
                        +{node.metadata.learning_objectives.length - 3} more
                      </Badge>
                    )}
                  </div>
                </div>
              )}

              {/* ✅ ADD: Questions preview */}
              {node.metadata?.questions && node.metadata.questions.length > 0 && (
                <div className="mt-2">
                  <div className="text-xs text-muted-foreground font-medium">
                    Includes {node.metadata.questions.length} quiz question{node.metadata.questions.length > 1 ? 's' : ''}
                  </div>
                </div>
              )}

              {/* ✅ ADD: Practice exercises preview */}
              {node.metadata?.practice_exercises && node.metadata.practice_exercises.length > 0 && (
                <div className="mt-2">
                  <div className="text-xs text-muted-foreground font-medium">
                    Includes {node.metadata.practice_exercises.length} practice exercise{node.metadata.practice_exercises.length > 1 ? 's' : ''}
                  </div>
                </div>
              )}
            </div>

            {/* Action Button */}
            <div className="flex-shrink-0">
              {node.status === 'current' && (
                <Button onClick={onStart} className="gap-2">
                  <PlayCircle className="h-4 w-4" />
                  Start
                </Button>
              )}
              {node.status === 'completed' && (
                <Button variant="outline" disabled className="gap-2">
                  <CheckCircle2 className="h-4 w-4" />
                  Completed
                </Button>
              )}
              {node.status === 'locked' && (
                <Button variant="outline" disabled className="gap-2">
                  <Lock className="h-4 w-4" />
                  Locked
                </Button>
              )}
              {node.status === 'unlocked' && !isCurrent && (
                <Button variant="outline" onClick={onStart} className="gap-2">
                  <PlayCircle className="h-4 w-4" />
                  Start
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};