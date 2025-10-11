import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { CalendarIcon, Upload, X, Loader2, Sparkles } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { supabase } from "../lib/supabaseClient";
import { useAuth } from "../store/AuthContext";

interface CreateGoalDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onGoalCreated: () => void;
}

export const CreateGoalDialog = ({ open, onOpenChange, onGoalCreated }: CreateGoalDialogProps) => {
  const { user } = useAuth();
  const [goalData, setGoalData] = useState({
    title: "",
    subject: "",
    goalType: "",
    duration: "",
    description: "",
    learningStyle: "",
    difficulty: "",
    weeks: 4,
    focus: "balanced",
    targetDate: undefined as Date | undefined,
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
  if (!user) {
    alert("Error: You must be logged in to create a goal. Please try logging in again.");
    return;
  }
  
  if (!goalData.title || !goalData.subject || !goalData.goalType || !goalData.learningStyle || !goalData.difficulty) {
    alert("Please fill in all required fields.");
    return;
  }

  setIsLoading(true);

  try {
    // 1. Find or create the category in Supabase
    let { data: category, error: categoryError } = await supabase
      .from('categories')
      .select('id')
      .eq('name', goalData.subject)
      .single();

    if (categoryError && categoryError.code !== 'PGRST116') { // PGRST116: row not found
      throw categoryError;
    }

    if (!category) {
      const { data: newCategory, error: newCategoryError } = await supabase
        .from('categories')
        .insert({ name: goalData.subject })
        .select('id')
        .single();
      if (newCategoryError) throw newCategoryError;
      category = newCategory;
    }

    // 2. Create the learning goal first (this table uses UUID for category_id)
    const { data: learningGoal, error: goalError } = await supabase
      .from('learning_goals')
      .insert({
        user_id: user.id,
        category_id: category.id, // This is UUID - correct for learning_goals table
        title: goalData.title,
        description: goalData.description,
        goal_type: goalData.goalType,
        learning_style: goalData.learningStyle,
        difficulty: goalData.difficulty,
        focus_type: goalData.focus,
        study_duration_hours: parseInt(goalData.duration) || 5,
        target_weeks: goalData.weeks,
        target_date: goalData.targetDate,
        status: 'active',
        progress: 0,
      })
      .select()
      .single();

    if (goalError) throw goalError;

    // 3. Now create the user_progress record with the correct category_id type
    // For user_progress, we need to use a bigint category_id or leave it null
    const { error: progressError } = await supabase
      .from('user_progress')
      .insert({
        user_id: user.id,
        category_id: category.id,
        course_name: goalData.title,
        progress_percent: 0,
      });

    if (progressError) {
      console.warn("Could not create user_progress record:", progressError);
      // Continue anyway since the main goal was created
    }

    console.log("Goal created successfully in Supabase!");
    alert(`Goal created successfully! Your ${goalData.subject} learning path has been created.`);

    onGoalCreated(); // Refresh the dashboard
    onOpenChange(false); // Close the dialog
    
    try {
      // Try to create a course via backend to obtain a course id
      const profile = user.user_metadata || {};
      const res = await (await import("@/lib/agentService")).default.createCourse({
        user_id: user.id,
        subject: goalData.subject,
        topic: goalData.title,
        weeks: goalData.weeks,
        focus: goalData.focus,
        assessments: true,
        user_profile: {
          name: profile.full_name || profile.name || "Learner",
          email: user.email || `${user.id}@example.com`,
          learning_style: goalData.learningStyle || "balanced",
          preferred_difficulty: goalData.difficulty || "intermediate",
          available_time: parseInt(goalData.duration || "60"),
          learning_goals: [goalData.description || "Learn the subject"],
          interests: [],
        },
      });
      if (res?.course_id) {
        window.open(`/course/${res.course_id}`, "_blank");
      }
    } catch (e) {
      console.warn("Course creation failed; skipping open tab.", e);
    }
    
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
      focus: "balanced",
      targetDate: undefined,
    });
    setUploadedFiles([]);

  } catch (error: any) {
    console.error("Error creating goal:", error.message);
    alert(`Error creating goal: ${error.message}`);
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

        <div className="p-6 space-y-6">
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
                    "p-4 border rounded-lg cursor-pointer transition-all hover:shadow-lg",
                    goalData.goalType === type.value
                      ? "border-primary bg-primary/10 shadow-md"
                      : "hover:bg-muted/50"
                  )}
                  onClick={() => setGoalData({...goalData, goalType: type.value})}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">{type.label}</h4>
                      <p className="text-sm text-muted-foreground">{type.description}</p>
                    </div>
                    {goalData.goalType === type.value && (
                      <Badge>Selected</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
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
              <Label>Target Completion Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant={"outline"}
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !goalData.targetDate && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {goalData.targetDate ? format(goalData.targetDate, "PPP") : <span>Pick a date</span>}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={goalData.targetDate}
                    onSelect={(date) => setGoalData({ ...goalData, targetDate: date as Date | undefined })}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
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
                      ? "border-primary bg-primary/10 shadow-md" 
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
                      <Badge>Selected</Badge>
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
                      ? "border-primary bg-primary/10 shadow-md" 
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
                      <Badge>Selected</Badge>
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
                      ? "border-primary bg-primary/10 shadow-md" 
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
                      <Badge>Selected</Badge>
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
            <div className="border-2 border-dashed rounded-lg p-6 text-center hover:border-primary/50">
              <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
              <p className="text-sm text-muted-foreground mb-2">Upload PDFs, notes, or other study materials</p>
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
