import React from 'react';
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
  BarChart3
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
                <Badge variant="outline" className="text-xs">
                  {node.duration} min
                </Badge>
                <Badge variant="secondary" className="text-xs capitalize">
                  {node.difficulty}
                </Badge>
                <Badge variant="outline" className="text-xs capitalize">
                  {node.type}
                </Badge>
              </div>

              {/* Prerequisites */}
              {node.prerequisites && node.prerequisites.length > 0 && (
                <div className="text-xs text-muted-foreground mb-3">
                  Requires: {node.prerequisites.join(', ')}
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