import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";
import { CalendarIcon, Upload, X } from "lucide-react";
import { format } from "date-fns";
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
    targetDate: undefined as Date | undefined,
  });
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);

  const subjects = [
    "Mathematics", "Physics", "Chemistry", "Biology", "Computer Science",
    "History", "Literature", "Psychology", "Economics", "Philosophy"
  ];

  const goalTypes = [
    { value: "revision", label: "Revision", description: "Review previously learned material" },
    { value: "new_learning", label: "New Learning", description: "Learn completely new topics" },
    { value: "exam_prep", label: "Exam Preparation", description: "Focused preparation for upcoming exams" }
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

  const handleCreateGoal = () => {
    console.log("Creating goal:", goalData, "Files:", uploadedFiles);
    onOpenChange(false);
    setGoalData({
      title: "",
      subject: "",
      goalType: "",
      duration: "",
      description: "",
      targetDate: undefined,
    });
    setUploadedFiles([]);
  };

  const cardClasses = "bg-[rgba(30,30,35,0.75)] backdrop-blur-md border border-gray-700 shadow-lg rounded-2xl transition-all duration-300";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">Create Learning Goal</DialogTitle>
          <DialogDescription>
            Set up a new learning objective with AI-powered guidance and progress tracking
          </DialogDescription>
        </DialogHeader>

        <div className="min-h-screen 
    bg-gradient-to-b from-gray-50 to-white text-gray-900
    dark:from-[#0f0f11] dark:to-[#1a1a1f] dark:text-gray-100
    p-6 space-y-6 transition-colors
  ">
          <div className="space-y-2">
            <Label htmlFor="title">Goal Title</Label>
            <Input
              id="title"
              placeholder="e.g., Master Calculus Fundamentals"
              value={goalData.title}
              onChange={(e) => setGoalData({...goalData, title: e.target.value})}
              className="bg-white text-gray-900 placeholder-gray-500 
             dark:bg-gray-800 dark:text-white dark:placeholder-gray-400 
             focus:border-blue-500"
            />
          </div>

          <div className="space-y-2">
            <Label>Subject</Label>
            <Select value={goalData.subject} onValueChange={(value) => setGoalData({...goalData, subject: value})}>
              <SelectTrigger className="bg-white text-gray-900 placeholder-gray-500 
             dark:bg-gray-800 dark:text-white dark:placeholder-gray-400 
             focus:border-blue-500">
                <SelectValue placeholder="Select a subject" />
              </SelectTrigger>
              <SelectContent className="bg-white text-gray-900 placeholder-gray-500 
             dark:bg-gray-800 dark:text-white dark:placeholder-gray-400 
             focus:border-blue-500">
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
                    "p-4 border rounded-lg cursor-pointer transition-all hover:shadow-xl hover:bg-gray-700/50",
                    goalData.goalType === type.value 
                      ? "border-blue-500 bg-blue-500/10 shadow-md" 
                      : "border-gray-700"
                  )}
                  onClick={() => setGoalData({...goalData, goalType: type.value})}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">{type.label}</h4>
                      <p className="text-sm text-gray-400">{type.description}</p>
                    </div>
                    {goalData.goalType === type.value && (
                      <Badge variant="default">Selected</Badge>
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
                className="bg-white text-gray-900 placeholder-gray-500 
             dark:bg-gray-800 dark:text-white dark:placeholder-gray-400 
             focus:border-blue-500"
              />
            </div>
            <div className="space-y-2">
              <Label>Target Completion Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal bg-white-800 text-gray-900 placeholder-gray-500 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400",
                      !goalData.targetDate && "text-gray-400"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {goalData.targetDate ? format(goalData.targetDate, "PPP") : "Pick a date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0 bg-gray-800 text-white">
                  <Calendar
                    mode="single"
                    selected={goalData.targetDate}
                    onSelect={(date) => setGoalData({...goalData, targetDate: date})}
                    initialFocus
                    className="bg-white text-gray-900 dark:bg-gray-800 dark:text-white"
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
              className="bg-white text-gray-900 placeholder-gray-500 
             dark:bg-gray-800 dark:text-white dark:placeholder-gray-400 
             focus:border-blue-500"
            />
          </div>

          <div className="space-y-3">
            <Label>Upload Study Materials (Optional)</Label>
            <div className="border-2 border-dashed border-gray-700 rounded-lg p-6 text-center transition-all hover:shadow-xl hover:bg-gray-700/50">
              <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm text-gray-400 mb-2">Upload PDFs, notes, or other study materials</p>
              <input
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <Button variant="outline" asChild className="bg-gray-800 text-white hover:bg-gradient-to-r hover:from-blue-500 hover:to-purple-500">
                <label htmlFor="file-upload" className="cursor-pointer">Choose Files</label>
              </Button>
            </div>
            
            {uploadedFiles.length > 0 && (
              <div className="space-y-2">
                <Label>Uploaded Files:</Label>
                <div className="flex flex-wrap gap-2">
                  {uploadedFiles.map((fileName, index) => (
                    <Badge key={index} variant="secondary" className="gap-1 bg-white text-gray-900 placeholder-gray-500 
             dark:bg-gray-800 dark:text-white dark:placeholder-gray-400 
             focus:border-blue-500">
                      {fileName}
                      <X className="w-3 h-3 cursor-pointer" onClick={() => removeFile(fileName)} />
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={() => onOpenChange(false)} className="flex-1 bg-white-800 text-gray-900 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400  focus:border-blue-500">
              Cancel
            </Button>
            <Button 
              onClick={handleCreateGoal} 
              className="flex-1 bg-gray-800 text-white hover:bg-gradient-to-r hover:from-blue-500 hover:to-purple-500"
              disabled={!goalData.title || !goalData.subject || !goalData.goalType}
            >
              Create Goal
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
