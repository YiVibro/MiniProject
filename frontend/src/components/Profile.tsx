import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { User, Edit3, Save, X, Trophy, Target, Clock, BookOpen, Award, TrendingUp, Calendar, Brain, Zap } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { motion, Variants, easeInOut } from "framer-motion";

export const Profile = () => {
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({
    name: "Alex Johnson",
    email: "alex.johnson@email.com",
    bio: "Passionate student pursuing computer science with a focus on AI and machine learning.",
    studyGoal: "Master advanced algorithms and data structures",
    preferredSubjects: ["Computer Science", "Mathematics", "Physics"],
    studyHours: 25,
    weeklyGoal: 30
  });
  const [editData, setEditData] = useState(profileData);

  const achievements = [
    { id: 1, title: "First Goal Completed", description: "Completed your first learning goal", icon: Target, earned: true },
    { id: 2, title: "Study Streak", description: "Studied for 7 consecutive days", icon: Calendar, earned: true },
    { id: 3, title: "AI Assistant Pro", description: "Had 50+ conversations with AI tutor", icon: Brain, earned: true },
    { id: 4, title: "Knowledge Master", description: "Completed 10 courses", icon: BookOpen, earned: false },
    { id: 5, title: "Speed Learner", description: "Completed a course in under 2 weeks", icon: Zap, earned: false }
  ];

  const stats = [
    { label: "Total Study Hours", value: "142", icon: Clock, color: "text-blue-500" },
    { label: "Courses Completed", value: "8", icon: Trophy, color: "text-yellow-500" },
    { label: "Current Streak", value: "12 days", icon: TrendingUp, color: "text-green-500" },
    { label: "AI Interactions", value: "89", icon: Brain, color: "text-purple-500" }
  ];

  const handleSave = () => {
    setProfileData(editData);
    setIsEditing(false);
    toast({ title: "Profile Updated", description: "Your profile has been successfully updated." });
  };

  const handleCancel = () => { 
    setEditData(profileData); 
    setIsEditing(false); 
  };

  const cardVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: easeInOut } }
  };

  const achievementVariants: Variants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: (i: number) => ({ opacity: 1, scale: 1, transition: { delay: i * 0.2, duration: 0.7, ease: easeInOut } }),
  };

  return (
    <motion.div className="p-4 sm:p-6 space-y-6 max-w-6xl mx-auto" initial="hidden" animate="visible" variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.1 }}}}>
      
      {/* Header */}
      <motion.div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4 sm:gap-0" variants={cardVariants}>
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold flex items-center gap-2 text-foreground dark:text-white">
            <User className="w-7 h-7 text-primary"/>My Profile
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground dark:text-gray-300">Manage your account and track your learning journey</p>
        </div>
        <Button onClick={() => setIsEditing(!isEditing)} variant={isEditing ? "outline" : "default"} className="gap-2">
          {isEditing ? <><X className="w-4 h-4"/> Cancel</> : <><Edit3 className="w-4 h-4"/> Edit Profile</>}
        </Button>
      </motion.div>

      {/* Personal Info & Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Personal Info */}
        <motion.div className="lg:col-span-2 space-y-6" variants={cardVariants}>
          <div className="relative">
            <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-purple-400 via-blue-400 to-pink-400 opacity-10 dark:opacity-30 blur-3xl pointer-events-none"></div>
            <Card className="relative bg-white dark:bg-gray-800/80 backdrop-blur-md shadow-lg border border-gray-200 dark:border-gray-700 hover:scale-105 transition-transform duration-500 ease-in-out">
              <CardHeader><CardTitle>Personal Information</CardTitle></CardHeader>
              <CardContent className="space-y-6">
                <motion.div className="flex flex-col sm:flex-row items-center sm:items-start gap-4 sm:gap-6" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }}>
                  <Avatar className="w-20 h-20">
                    <AvatarImage src="/placeholder-avatar.jpg"/>
                    <AvatarFallback>{profileData.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                  </Avatar>
                  {isEditing && <Button variant="outline" size="sm">Change Photo</Button>}
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    {isEditing ? <Input id="name" value={editData.name} onChange={e => setEditData({...editData, name: e.target.value})}/> : <p className="p-2 bg-gray-100 dark:bg-gray-700 rounded-md">{profileData.name}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    {isEditing ? <Input id="email" type="email" value={editData.email} onChange={e => setEditData({...editData, email: e.target.value})}/> : <p className="p-2 bg-gray-100 dark:bg-gray-700 rounded-md">{profileData.email}</p>}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bio">Bio</Label>
                  {isEditing ? <Textarea id="bio" value={editData.bio} onChange={e => setEditData({...editData, bio:e.target.value})} rows={3}/> : <p className="p-2 bg-gray-100 dark:bg-gray-700 rounded-md">{profileData.bio}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="studyGoal">Current Study Goal</Label>
                  {isEditing ? <Input id="studyGoal" value={editData.studyGoal} onChange={e => setEditData({...editData, studyGoal:e.target.value})}/> : <p className="p-2 bg-gray-100 dark:bg-gray-700 rounded-md">{profileData.studyGoal}</p>}
                </div>

                <div className="space-y-2">
                  <Label>Preferred Subjects</Label>
                  <div className="flex flex-wrap gap-2">
                    {profileData.preferredSubjects.map(s => <Badge key={s} variant="secondary">{s}</Badge>)}
                    {isEditing && <Button variant="outline" size="sm">+ Add Subject</Button>}
                  </div>
                </div>

                {isEditing && <div className="flex flex-wrap gap-2 pt-4">
                  <Button onClick={handleSave} className="gap-2"><Save className="w-4 h-4"/> Save Changes</Button>
                  <Button variant="outline" onClick={handleCancel}>Cancel</Button>
                </div>}
              </CardContent>
            </Card>
          </div>
        </motion.div>

        {/* Stats Column */}
        <motion.div className="space-y-6" variants={cardVariants}>
          {/* Study Statistics */}
          <div className="relative">
            <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-green-200 via-green-300 to-blue-300 opacity-10 dark:opacity-30 blur-3xl pointer-events-none"></div>
            <Card className="relative bg-white dark:bg-gray-800/80 backdrop-blur-md shadow-lg border border-gray-200 dark:border-gray-700 hover:scale-105 transition-transform duration-500 ease-in-out">
              <CardHeader><CardTitle className="text-lg">Study Statistics</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                {stats.map((s, i) => (
                  <motion.div key={s.label} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.2, duration: 0.8, ease: easeInOut }} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <s.icon className={`w-4 h-4 ${s.color}`} />
                      <span className="text-sm text-muted-foreground dark:text-gray-300">{s.label}</span>
                    </div>
                    <span className="font-semibold">{s.value}</span>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Weekly Goal */}
          <div className="relative">
            <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-purple-200 via-pink-200 to-yellow-200 opacity-10 dark:opacity-30 blur-3xl pointer-events-none"></div>
            <Card className="relative bg-white dark:bg-gray-800/80 backdrop-blur-md shadow-lg border border-gray-200 dark:border-gray-700 hover:scale-105 transition-transform duration-500 ease-in-out">
              <CardHeader><CardTitle className="text-lg">Weekly Goal</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Study Hours</span>
                    <span>{profileData.studyHours}/{profileData.weeklyGoal} hrs</span>
                  </div>
                  <motion.div initial={{ width: 0 }} animate={{ width: (profileData.studyHours/profileData.weeklyGoal)*100 + "%" }} transition={{ duration: 1, ease: easeInOut }}>
                    <Progress value={(profileData.studyHours/profileData.weeklyGoal)*100} className="h-2"/>
                  </motion.div>
                </div>
                <p className="text-xs text-muted-foreground dark:text-gray-300">{profileData.weeklyGoal - profileData.studyHours} hours remaining this week</p>
              </CardContent>
            </Card>
          </div>
        </motion.div>
      </div>

      {/* Achievements */}
      <div className="relative">
        <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-yellow-200 via-pink-200 to-purple-200 opacity-10 dark:opacity-30 blur-3xl pointer-events-none"></div>
        <Card className="relative bg-white dark:bg-gray-800/80 backdrop-blur-md shadow-lg border border-gray-200 dark:border-gray-700 hover:scale-105 transition-transform duration-500 ease-in-out">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="w-5 h-5 text-primary"/>Achievements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {achievements.map((a, i) => (
                <motion.div key={a.id} custom={i} initial="hidden" animate="visible" variants={achievementVariants} className={`p-4 rounded-lg border transition-all ${a.earned ? 'bg-primary/5 border-primary/20 dark:ring-2 dark:ring-primary/50 dark:shadow-lg' : 'bg-gray-100 dark:bg-gray-700/50 border-gray-200 dark:border-gray-600 opacity-60'}`}>
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-full ${a.earned ? 'bg-primary text-primary-foreground dark:bg-primary dark:text-white' : 'bg-gray-200 dark:bg-gray-600 text-gray-500'}`}>
                      <a.icon className="w-4 h-4"/>
                    </div>
                    <div className="space-y-1 flex-1">
                      <h4 className="font-medium text-sm">{a.title}</h4>
                      <p className="text-xs text-muted-foreground dark:text-gray-300">{a.description}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
};
