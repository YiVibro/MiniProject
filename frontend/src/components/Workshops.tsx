import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Users, Clock, Calendar, Play, BookOpen, Star, Bot, Send, Plus, 
  CheckCircle, Lightbulb 
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

interface Workshop {
  id: string;
  title: string;
  description: string;
  instructor: string;
  subject: string;
  duration: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  rating: number;
  enrolled: number;
  maxEnrollment: number;
  startDate: string;
  topics: string[];
  isEnrolled: boolean;
  progress?: number;
}

interface Task {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed';
  subject: string;
  difficulty: 'easy' | 'medium' | 'hard';
  estimatedTime: string;
  aiSuggestions?: string[];
  notes?: string;
}

interface AIMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

export const Workshops = () => {
  const { toast } = useToast();
  const [activeTask, setActiveTask] = useState<Task | null>(null);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskDescription, setNewTaskDescription] = useState("");
  const [aiMessages, setAiMessages] = useState<AIMessage[]>([
    {
      id: '1',
      type: 'ai',
      content: "Hello! I'm your AI study companion. I'll help track your learning progress and provide suggestions whenever you need them. What would you like to learn today?",
      timestamp: new Date()
    }
  ]);
  const [newMessage, setNewMessage] = useState("");

  const [tasks, setTasks] = useState<Task[]>([
    {
      id: '1',
      title: 'Complete Linear Algebra Assignment',
      description: 'Solve problems 1-15 from Chapter 3: Matrix Operations',
      status: 'in-progress',
      subject: 'Mathematics',
      difficulty: 'medium',
      estimatedTime: '2 hours',
      aiSuggestions: [
        'Break down matrix multiplication into smaller steps',
        'Use the Khan Academy linear algebra course for reference',
        'Practice with simpler 2x2 matrices first'
      ],
      notes: 'Struggling with 3x3 matrix determinants'
    },
    {
      id: '2',
      title: 'Physics Lab Report',
      description: 'Write lab report on pendulum motion experiment',
      status: 'pending',
      subject: 'Physics',
      difficulty: 'medium',
      estimatedTime: '3 hours',
      aiSuggestions: [
        'Include graphs showing period vs length relationship',
        'Discuss sources of experimental error',
        "Reference Newton's laws in your analysis"
      ]
    },
    {
      id: '3',
      title: 'Learn React Hooks',
      description: 'Understand useState, useEffect, and custom hooks',
      status: 'completed',
      subject: 'Computer Science',
      difficulty: 'hard',
      estimatedTime: '4 hours',
      notes: 'Completed! Custom hooks are very powerful for reusable logic.'
    }
  ]);

  const workshops: Workshop[] = [
    {
      id: '1',
      title: 'Advanced Calculus Masterclass',
      description: 'Deep dive into differential and integral calculus with real-world applications. Perfect for exam preparation.',
      instructor: 'Dr. Sarah Chen',
      subject: 'Mathematics',
      duration: '6 weeks',
      difficulty: 'Advanced',
      rating: 4.8,
      enrolled: 245,
      maxEnrollment: 300,
      startDate: '2024-02-01',
      topics: ['Limits', 'Derivatives', 'Integrals', 'Applications'],
      isEnrolled: true,
      progress: 65
    },
    {
      id: '2',
      title: 'Physics Problem Solving Techniques',
      description: 'Learn systematic approaches to solve complex physics problems across mechanics, thermodynamics, and more.',
      instructor: 'Prof. Michael Rodriguez',
      subject: 'Physics',
      duration: '4 weeks',
      difficulty: 'Intermediate',
      rating: 4.6,
      enrolled: 189,
      maxEnrollment: 250,
      startDate: '2024-02-15',
      topics: ['Mechanics', 'Thermodynamics', 'Electromagnetism', 'Optics'],
      isEnrolled: false
    },
    {
      id: '3',
      title: 'Organic Chemistry Fundamentals',
      description: 'Master the basics of organic chemistry with interactive sessions and practical examples.',
      instructor: 'Dr. Emily Watson',
      subject: 'Chemistry',
      duration: '8 weeks',
      difficulty: 'Beginner',
      rating: 4.9,
      enrolled: 156,
      maxEnrollment: 200,
      startDate: '2024-01-20',
      topics: ['Structure', 'Reactions', 'Mechanisms', 'Synthesis'],
      isEnrolled: true,
      progress: 30
    },
    {
      id: '4',
      title: 'Data Structures and Algorithms',
      description: 'Essential programming concepts for computer science students and coding interviews.',
      instructor: 'Alex Thompson',
      subject: 'Computer Science',
      duration: '10 weeks',
      difficulty: 'Intermediate',
      rating: 4.7,
      enrolled: 320,
      maxEnrollment: 400,
      startDate: '2024-02-10',
      topics: ['Arrays', 'Trees', 'Graphs', 'Sorting', 'Dynamic Programming'],
      isEnrolled: false
    }
  ];

  const enrolledWorkshops = workshops.filter(w => w.isEnrolled);
  const availableWorkshops = workshops.filter(w => !w.isEnrolled);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner': return 'bg-emerald-500/10 text-emerald-600 dark:bg-emerald-600/20 dark:text-emerald-300';
      case 'Intermediate': return 'bg-amber-500/10 text-amber-600 dark:bg-amber-600/20 dark:text-amber-300';
      case 'Advanced': return 'bg-rose-500/10 text-rose-600 dark:bg-rose-600/20 dark:text-rose-300';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getTaskDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-emerald-500/10 text-emerald-600 dark:bg-emerald-600/20 dark:text-emerald-300';
      case 'medium': return 'bg-amber-500/10 text-amber-600 dark:bg-amber-600/20 dark:text-amber-300';
      case 'hard': return 'bg-rose-500/10 text-rose-600 dark:bg-rose-600/20 dark:text-rose-300';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-emerald-500/10 text-emerald-600 dark:bg-emerald-600/20 dark:text-emerald-300';
      case 'in-progress': return 'bg-blue-500/10 text-blue-600 dark:bg-blue-600/20 dark:text-blue-300';
      case 'pending': return 'bg-muted text-muted-foreground';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const addNewTask = () => {
    if (!newTaskTitle.trim()) return;
    const newTask: Task = {
      id: Date.now().toString(),
      title: newTaskTitle,
      description: newTaskDescription,
      status: 'pending',
      subject: 'General',
      difficulty: 'medium',
      estimatedTime: '1 hour',
      aiSuggestions: [
        'Break this task into smaller, manageable steps',
        'Set a timer to maintain focus',
        'Take notes as you progress'
      ]
    };
    setTasks([newTask, ...tasks]);
    setNewTaskTitle("");
    setNewTaskDescription("");
    setActiveTask(newTask);
    toast({
      title: "Task Created",
      description: "Your new learning task has been added and AI suggestions are ready!",
    });
  };

  const updateTaskStatus = (taskId: string, newStatus: Task['status']) => {
    setTasks(tasks.map(task => 
      task.id === taskId ? { ...task, status: newStatus } : task
    ));
    if (newStatus === 'completed') {
      toast({
        title: "Task Completed!",
        description: "Great job! Your progress has been tracked.",
      });
    }
  };

  const sendAIMessage = () => {
    if (!newMessage.trim()) return;
    const userMessage: AIMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: newMessage,
      timestamp: new Date()
    };
    setAiMessages([...aiMessages, userMessage]);
    setNewMessage("");
    setTimeout(() => {
      const aiResponse: AIMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: generateAIResponse(newMessage),
        timestamp: new Date()
      };
      setAiMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  const generateAIResponse = (userMessage: string): string => {
    const responses = [
      "That's a great question! Let me help you break this down into manageable steps.",
      "I understand you're working on this topic. Here's a strategy that often works well...",
      "Based on your learning pattern, I'd suggest focusing on the fundamental concepts first.",
      "This is a common challenge. Many students find it helpful to practice with examples.",
      "Let's approach this systematically. What specific part are you finding most difficult?",
      "I notice you're making good progress! Here's how to tackle the next section effectively."
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  return (
    <div className="p-4 sm:p-6 space-y-6 bg-background dark:bg-gray-900 text-foreground dark:text-gray-100 transition-colors">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold flex items-center gap-2">
            <BookOpen className="w-7 h-7 text-primary" /> AI-Powered Learning Studio
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground dark:text-gray-400">
            Learn anything you want with AI tracking and personalized suggestions
          </p>
        </div>
        <Button variant="hero" className="gap-2">
          <Bot className="w-4 h-4" /> AI Assistant
        </Button>
      </div>

      {/* Main Content */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left: Tasks */}
        <div className="flex-1 space-y-6">
          {/* New Task Card */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
            <Card className="bg-card dark:bg-gray-800 border border-border dark:border-gray-700 shadow-sm hover:shadow-md transition">
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Plus className="w-5 h-5 text-primary"/> Create Learning Task</CardTitle>
                <CardDescription>Tell the AI what you want to learn and it will track your progress</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="What do you want to learn? (e.g., 'Learn Python basics')"
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  className="bg-background dark:bg-gray-700 border border-border dark:border-gray-600 text-foreground dark:text-gray-200"
                />
                <Textarea
                  placeholder="Add more details about your learning goal..."
                  value={newTaskDescription}
                  onChange={(e) => setNewTaskDescription(e.target.value)}
                  rows={2}
                  className="bg-background dark:bg-gray-700 border border-border dark:border-gray-600 text-foreground dark:text-gray-200"
                />
                <Button
                  onClick={addNewTask}
                  variant="outline"
                  size="sm"
                  className="w-full mt-2 bg-card dark:bg-gray-800 text-foreground dark:text-gray-100 border border-border dark:border-gray-600 hover:bg-gradient-to-r hover:from-blue-500 hover:to-purple-500 hover:text-white transition-all duration-300"
                >
                  <Plus className="w-4 h-4" /> Start Learning
                </Button>
              </CardContent>
            </Card>
          </motion.div>

          {/* Active Tasks */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ staggerChildren: 0.1 }}>
            <Card className="bg-card dark:bg-gray-800 border border-border dark:border-gray-700 shadow-sm hover:shadow-md transition">
              <CardHeader>
                <CardTitle>Your Learning Tasks</CardTitle>
                <CardDescription>AI-tracked learning activities with personalized suggestions</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 max-h-[500px] overflow-y-auto">
                {tasks.map(task => (
                  <motion.div key={task.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} whileHover={{ scale: 1.02 }} transition={{ duration: 0.3 }}>
                    <Card
                      className={`cursor-pointer transition-all ${activeTask?.id === task.id ? 'ring-2 ring-primary' : 'hover:shadow-md'}`}
                      onClick={() => setActiveTask(task)}
                    >
                      <CardContent className="p-4">
                        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                          <div className="space-y-2 flex-1">
                            <div className="flex items-center gap-2 flex-wrap">
                              <h4 className="font-medium">{task.title}</h4>
                              <Badge className={getStatusColor(task.status)}>{task.status}</Badge>
                              <Badge className={getTaskDifficultyColor(task.difficulty)}>{task.difficulty}</Badge>
                            </div>
                            <p className="text-sm text-muted-foreground dark:text-gray-400">{task.description}</p>
                            {task.aiSuggestions && task.aiSuggestions.length > 0 && (
                              <div className="flex flex-wrap gap-2 mt-1">
                                {task.aiSuggestions.map((s, idx) => (
                                  <Badge key={idx} className="bg-blue-100 text-blue-700 dark:bg-blue-700/20 dark:text-blue-200">{s}</Badge>
                                ))}
                              </div>
                            )}
                          </div>
                          <div className="flex gap-2">
                            {task.status !== 'completed' && (
                              <Button size="sm" onClick={() => updateTaskStatus(task.id, 'completed')}>
                                <CheckCircle className="w-4 h-4 mr-1" /> Complete
                              </Button>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Right: AI Chat / Workshops */}
        <div className="flex-1 flex flex-col gap-6">
          {/* AI Chat */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <Card className="bg-card dark:bg-gray-800 border border-border dark:border-gray-700 shadow-sm hover:shadow-md transition flex flex-col h-[500px]">
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Bot className="w-5 h-5 text-primary"/> AI Study Companion</CardTitle>
                <CardDescription>Get guidance, suggestions, and track your progress</CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col overflow-hidden">
                <ScrollArea className="flex-1 space-y-3 py-2">
                  {aiMessages.map(msg => (
                    <div key={msg.id} className={`p-2 rounded-md max-w-[80%] ${msg.type === 'user' ? 'bg-blue-500/10 text-blue-600 dark:bg-blue-600/20 dark:text-blue-300 ml-auto' : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'}`}>
                      <p className="text-sm">{msg.content}</p>
                    </div>
                  ))}
                </ScrollArea>
                <div className="mt-2 flex gap-2">
                  <Input
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-1 bg-background dark:bg-gray-700 border border-border dark:border-gray-600 text-foreground dark:text-gray-200"
                  />
                  <Button onClick={sendAIMessage}><Send className="w-4 h-4" /></Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Enrolled Workshops */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <Card className="bg-card dark:bg-gray-800 border border-border dark:border-gray-700 shadow-sm hover:shadow-md transition">
              <CardHeader>
                <CardTitle>Your Workshops</CardTitle>
                <CardDescription>Track your progress and topics</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[400px] overflow-y-auto">
                {enrolledWorkshops.map(w => (
                  <Card key={w.id} className="bg-card dark:bg-gray-800 border border-border dark:border-gray-700 p-4 flex flex-col gap-2">
                    <h4 className="font-semibold">{w.title}</h4>
                    <p className="text-sm text-muted-foreground dark:text-gray-400">{w.description}</p>
                    <div className="flex flex-wrap gap-1">
                      <Badge className={getDifficultyColor(w.difficulty)}>{w.difficulty}</Badge>
                      <Badge className="bg-blue-100 text-blue-700 dark:bg-blue-700/20 dark:text-blue-200">{w.subject}</Badge>
                    </div>
                    {w.progress !== undefined && <Progress value={w.progress} className="h-2 mt-2" />}
                  </Card>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
};
