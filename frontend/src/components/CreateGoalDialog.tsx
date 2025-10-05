import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { CalendarIcon, Upload, X, Loader2, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface CreateGoalDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const CreateGoalDialog = ({ open, onOpenChange }: CreateGoalDialogProps) => {
  const [goalData, setGoalData] = useState({
    title: "",
    subject: "",
    goalType: "",
    duration: "",
    description: "",
    learningStyle: "",
    difficulty: "",
    weeks: 4,
    focus: "balanced"
  });
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const subjects = [
    "Python Programming", "JavaScript", "Machine Learning", "Web Development", 
    "Data Science", "Computer Science", "Mathematics", "Physics", "Chemistry", "Biology"
  ];

  const goalTypes = [
    { value: "revision", label: "Revision", description: "Review previously learned material" },
    { value: "new_learning", label: "New Learning", description: "Learn completely new topics" },
    { value: "exam_prep", label: "Exam Preparation", description: "Focused preparation for upcoming exams" }
  ];

  const learningStyles = [
    { value: "visual", label: "Visual", description: "Learn through diagrams, charts, and visual aids" },
    { value: "auditory", label: "Auditory", description: "Learn through listening and verbal explanations" },
    { value: "kinesthetic", label: "Kinesthetic", description: "Learn through hands-on activities and movement" },
    { value: "analytical", label: "Analytical", description: "Learn through detailed analysis and logical structure" },
    { value: "practical", label: "Practical", description: "Learn through real-world applications" },
    { value: "balanced", label: "Balanced", description: "Mix of all learning styles" }
  ];

  const difficultyLevels = [
    { value: "beginner", label: "Beginner", description: "New to the subject" },
    { value: "intermediate", label: "Intermediate", description: "Some experience" },
    { value: "advanced", label: "Advanced", description: "Experienced learner" }
  ];

  const focusTypes = [
    { value: "theoretical", label: "Theory-focused", description: "Deep understanding of concepts" },
    { value: "practical", label: "Practice-focused", description: "Hands-on exercises and projects" },
    { value: "balanced", label: "Balanced", description: "Mix of theory and practice" },
    { value: "project-based", label: "Project-based", description: "Build real-world projects" }
  ];

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      const newFiles = Array.from(files).map(file => file.name);
      setUploadedFiles([...uploadedFiles, ...newFiles]);
    }
  };

  const removeFile = (fileName: string) => {
    setUploadedFiles(uploadedFiles.filter(file => file !== fileName));
  };

  const handleCreateGoal = async () => {
    if (!goalData.title || !goalData.subject || !goalData.goalType || !goalData.learningStyle || !goalData.difficulty) {
      alert("Please fill in all required fields.");
      return;
    }

    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      alert(`Goal created successfully! Your ${goalData.subject} learning path has been created.`);
      
      // Reset form
      setGoalData({
        title: "",
        subject: "",
        goalType: "",
        duration: "",
        description: "",
        learningStyle: "",
        difficulty: "",
        weeks: 4,
        focus: "balanced"
      });
      setUploadedFiles([]);
      onOpenChange(false);
      
    } catch (error) {
      console.error('Failed to create goal:', error);
      alert("Failed to create learning goal. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">Create Learning Goal</DialogTitle>
          <DialogDescription>
            Set up a new learning objective with AI-powered guidance and progress tracking
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="title">Goal Title</Label>
            <Input
              id="title"
              placeholder="e.g., Master Calculus Fundamentals"
              value={goalData.title}
              onChange={(e) => setGoalData({...goalData, title: e.target.value})}
            />
          </div>

          <div className="space-y-2">
            <Label>Subject</Label>
            <Select value={goalData.subject} onValueChange={(value) => setGoalData({...goalData, subject: value})}>
              <SelectTrigger>
                <SelectValue placeholder="Select a subject" />
              </SelectTrigger>
              <SelectContent>
                {subjects.map((subject) => (
                  <SelectItem key={subject} value={subject}>{subject}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-3">
            <Label>Goal Type</Label>
            <div className="grid gap-3">
              {goalTypes.map((type) => (
                <div
                  key={type.value}
                  className={cn(
                    "p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md",
                    goalData.goalType === type.value 
                      ? "border-blue-500 bg-blue-500/10 shadow-md" 
                      : "border-gray-300"
                  )}
                  onClick={() => setGoalData({...goalData, goalType: type.value})}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">{type.label}</h4>
                      <p className="text-sm text-gray-500">{type.description}</p>
                    </div>
                    {goalData.goalType === type.value && (
                      <Badge variant="default">Selected</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label>Study Duration (hours/week)</Label>
            <Input
              type="number"
              placeholder="e.g., 5"
              value={goalData.duration}
              onChange={(e) => setGoalData({...goalData, duration: e.target.value})}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description (Optional)</Label>
            <Textarea
              id="description"
              placeholder="Describe your learning objectives..."
              value={goalData.description}
              onChange={(e) => setGoalData({...goalData, description: e.target.value})}
              rows={3}
            />
          </div>

          {/* Learning Style Selection */}
          <div className="space-y-3">
            <Label>Learning Style</Label>
            <div className="grid gap-3">
              {learningStyles.map((style) => (
                <div
                  key={style.value}
                  className={cn(
                    "p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md",
                    goalData.learningStyle === style.value 
                      ? "border-blue-500 bg-blue-500/10 shadow-md" 
                      : "border-gray-300"
                  )}
                  onClick={() => setGoalData({...goalData, learningStyle: style.value})}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">{style.label}</h4>
                      <p className="text-sm text-gray-500">{style.description}</p>
                    </div>
                    {goalData.learningStyle === style.value && (
                      <Badge variant="default">Selected</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Difficulty Level Selection */}
          <div className="space-y-3">
            <Label>Difficulty Level</Label>
            <div className="grid gap-3">
              {difficultyLevels.map((level) => (
                <div
                  key={level.value}
                  className={cn(
                    "p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md",
                    goalData.difficulty === level.value 
                      ? "border-blue-500 bg-blue-500/10 shadow-md" 
                      : "border-gray-300"
                  )}
                  onClick={() => setGoalData({...goalData, difficulty: level.value})}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">{level.label}</h4>
                      <p className="text-sm text-gray-500">{level.description}</p>
                    </div>
                    {goalData.difficulty === level.value && (
                      <Badge variant="default">Selected</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Course Focus Selection */}
          <div className="space-y-3">
            <Label>Course Focus</Label>
            <div className="grid gap-3">
              {focusTypes.map((focus) => (
                <div
                  key={focus.value}
                  className={cn(
                    "p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md",
                    goalData.focus === focus.value 
                      ? "border-blue-500 bg-blue-500/10 shadow-md" 
                      : "border-gray-300"
                  )}
                  onClick={() => setGoalData({...goalData, focus: focus.value})}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">{focus.label}</h4>
                      <p className="text-sm text-gray-500">{focus.description}</p>
                    </div>
                    {goalData.focus === focus.value && (
                      <Badge variant="default">Selected</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Course Duration in Weeks */}
          <div className="space-y-2">
            <Label>Course Duration (weeks)</Label>
            <Select value={goalData.weeks.toString()} onValueChange={(value) => setGoalData({...goalData, weeks: parseInt(value)})}>
              <SelectTrigger>
                <SelectValue placeholder="Select duration" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="2">2 weeks (6 lessons)</SelectItem>
                <SelectItem value="4">1 month (12 lessons)</SelectItem>
                <SelectItem value="8">2 months (24 lessons)</SelectItem>
                <SelectItem value="12">3 months (36 lessons)</SelectItem>
                <SelectItem value="24">6 months (48 lessons)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-3">
            <Label>Upload Study Materials (Optional)</Label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center transition-all hover:shadow-md">
              <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm text-gray-500 mb-2">Upload PDFs, notes, or other study materials</p>
              <input
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <Button variant="outline" asChild>
                <label htmlFor="file-upload" className="cursor-pointer">Choose Files</label>
              </Button>
            </div>
            
            {uploadedFiles.length > 0 && (
              <div className="space-y-2">
                <Label>Uploaded Files:</Label>
                <div className="flex flex-wrap gap-2">
                  {uploadedFiles.map((fileName, index) => (
                    <Badge key={index} variant="secondary" className="gap-1">
                      {fileName}
                      <X className="w-3 h-3 cursor-pointer" onClick={() => removeFile(fileName)} />
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={() => onOpenChange(false)} className="flex-1">
              Cancel
            </Button>
            <Button 
              onClick={handleCreateGoal} 
              className="flex-1"
              disabled={!goalData.title || !goalData.subject || !goalData.goalType || !goalData.learningStyle || !goalData.difficulty || isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Create Goal
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};