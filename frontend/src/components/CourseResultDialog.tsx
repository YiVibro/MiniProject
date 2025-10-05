import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { BookOpen, Clock, Target, Star, Play, CheckCircle } from "lucide-react";
import { CourseResponse } from "@/lib/agentService";

interface CourseResultDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  courseData: CourseResponse | null;
}

export const CourseResultDialog = ({ open, onOpenChange, courseData }: CourseResultDialogProps) => {
  const [selectedLesson, setSelectedLesson] = useState(0);

  if (!courseData) return null;

  const { curriculum, learning_path, requirements } = courseData;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl flex items-center gap-2">
            <BookOpen className="h-6 w-6" />
            Your Learning Path is Ready!
          </DialogTitle>
          <DialogDescription>
            AI has created a personalized curriculum based on your preferences
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Course Overview */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 p-6 rounded-lg border">
            <h3 className="text-xl font-semibold mb-2">{learning_path.title}</h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">{learning_path.description}</p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex items-center gap-2">
                <BookOpen className="h-4 w-4 text-blue-600" />
                <div>
                  <p className="text-sm font-medium">{curriculum.length} Lessons</p>
                  <p className="text-xs text-gray-500">Total Content</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-green-600" />
                <div>
                  <p className="text-sm font-medium">{Math.round(learning_path.estimated_duration / 60)} Hours</p>
                  <p className="text-xs text-gray-500">Estimated Time</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-purple-600" />
                <div>
                  <p className="text-sm font-medium">{requirements.weeks} Weeks</p>
                  <p className="text-xs text-gray-500">Duration</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Star className="h-4 w-4 text-yellow-600" />
                <div>
                  <p className="text-sm font-medium">{requirements.focus}</p>
                  <p className="text-xs text-gray-500">Focus</p>
                </div>
              </div>
            </div>
          </div>

          {/* Course Details */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Course Curriculum</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {curriculum.map((lesson, index) => (
                <div 
                  key={lesson.id}
                  className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                    selectedLesson === index ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'bg-white dark:bg-gray-800'
                  }`}
                  onClick={() => setSelectedLesson(index)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium">{lesson.title}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                        {lesson.content.substring(0, 100)}...
                      </p>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <Badge variant="outline" className="text-xs">
                        {lesson.difficulty}
                      </Badge>
                      <Badge variant="secondary" className="text-xs">
                        {lesson.duration} min
                      </Badge>
                    </div>
                  </div>
                  
                  {selectedLesson === index && (
                    <div className="mt-4 space-y-3">
                      <div>
                        <h5 className="font-medium text-sm mb-2">Learning Objectives:</h5>
                        <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                          {lesson.learning_objectives.map((objective, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <CheckCircle className="h-3 w-3 mt-0.5 text-green-600 flex-shrink-0" />
                              {objective}
                            </li>
                          ))}
                        </ul>
                      </div>
                      {lesson.prerequisites.length > 0 && (
                        <div>
                          <h5 className="font-medium text-sm mb-2">Prerequisites:</h5>
                          <div className="flex flex-wrap gap-1">
                            {lesson.prerequisites.map((prereq, idx) => (
                              <Badge key={idx} variant="outline" className="text-xs">
                                {prereq}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Course Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg">
              <h4 className="font-medium mb-3">Subject & Focus</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Subject:</span>
                  <Badge variant="outline">{requirements.subject}</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Topic:</span>
                  <span className="text-sm">{requirements.topic}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Focus:</span>
                  <Badge variant="secondary">{requirements.focus}</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Assessments:</span>
                  <span className="text-sm">{requirements.assessments ? 'Included' : 'Not included'}</span>
                </div>
              </div>
            </div>

            <div className="p-4 border rounded-lg">
              <h4 className="font-medium mb-3">Learning Path Details</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Duration:</span>
                  <span className="text-sm">{requirements.weeks} weeks</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Lessons:</span>
                  <span className="text-sm">{curriculum.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Estimated Time:</span>
                  <span className="text-sm">{Math.round(learning_path.estimated_duration / 60)} hours</span>
                </div>
              </div>
            </div>
          </div>

          {/* Learning Milestones */}
          {learning_path.milestones && learning_path.milestones.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Learning Milestones</h3>
              <div className="space-y-3">
                {learning_path.milestones.map((milestone, index) => (
                  <div key={index} className="p-4 border rounded-lg">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                          {index + 1}
                        </span>
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{milestone}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={() => onOpenChange(false)} className="flex-1">
              Close
            </Button>
            <Button className="flex-1 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600">
              <Play className="mr-2 h-4 w-4" />
              Start Learning
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};