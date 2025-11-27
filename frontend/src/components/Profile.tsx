import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { User, Edit3, Save, X, Trophy, Target, Clock, BookOpen, Award, TrendingUp, Calendar, Brain, Zap, Loader2, Plus } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { motion, Variants, easeInOut } from "framer-motion";
import { useUserProfile } from "./hooks/useUserProfile";
import { XPProgressBar } from "./XPProgressBar";
import { ProfileImageUpload } from "./ProfileImageUpload";
import { useAuth } from "@/store/AuthContext";
import { Link } from "react-router-dom";

// Icon mapping for achievements
const iconMap: Record<string, any> = {
  Target,
  Calendar,
  Brain,
  BookOpen,
  Zap,
  Trophy,
  Award,
};

export const Profile = () => {
  const { toast } = useToast();
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [newSubject, setNewSubject] = useState("");

  const {
    profile,
    stats,
    achievements,
    loading,
    error,
    updateProfile,
    uploadAvatar,
    addSubject,
    removeSubject,
  } = useUserProfile();

  const [editData, setEditData] = useState({
    name: "",
    bio: "",
    study_goal: "",
    weekly_goal: 30,
  });

  // Update editData when profile loads
  useEffect(() => {
    if (profile) {
      setEditData({
        name: profile.name || "",
        bio: profile.bio || "",
        study_goal: profile.study_goal || "",
        weekly_goal: profile.weekly_goal || 30,
      });
    }
  }, [profile]);

  const handleSave = async () => {
    const result = await updateProfile(editData);
    if (result.success) {
      setIsEditing(false);
      toast({
        title: "Profile Updated",
        description: "Your profile has been successfully updated."
      });
    } else {
      toast({
        title: "Update Failed",
        description: result.error || "Failed to update profile",
        variant: "destructive"
      });
    }
  };

  const handleCancel = () => {
    if (profile) {
      setEditData({
        name: profile.name || "",
        bio: profile.bio || "",
        study_goal: profile.study_goal || "",
        weekly_goal: profile.weekly_goal || 30,
      });
    }
    setIsEditing(false);
  };

  const handleAddSubject = async () => {
    if (!newSubject.trim()) return;
    await addSubject(newSubject.trim());
    setNewSubject("");
    toast({
      title: "Subject Added",
      description: `${newSubject} has been added to your preferred subjects.`
    });
  };

  const handleRemoveSubject = async (subject: string) => {
    await removeSubject(subject);
    toast({
      title: "Subject Removed",
      description: `${subject} has been removed from your preferred subjects.`
    });
  };

  const cardVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: easeInOut } }
  };

  const achievementVariants: Variants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: (i: number) => ({ opacity: 1, scale: 1, transition: { delay: i * 0.2, duration: 0.7, ease: easeInOut } }),
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen w-full bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading profile...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen w-full bg-background flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Error Loading Profile</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // No profile state (shouldn't happen with auto-creation)
  if (!profile || !stats) {
    return (
      <div className="min-h-screen w-full bg-background flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>Profile Not Found</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Unable to load profile data.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const statsDisplay = [
    { label: "Total Study Hours", value: stats.total_study_hours.toString(), icon: Clock, color: "text-blue-500" },
    { label: "Courses Completed", value: stats.courses_completed.toString(), icon: Trophy, color: "text-yellow-500" },
    { label: "Current Streak", value: `${stats.current_streak} days`, icon: TrendingUp, color: "text-green-500" },
    { label: "AI Interactions", value: stats.ai_interactions.toString(), icon: Brain, color: "text-purple-500" }
  ];

  const weeklyProgress = (stats.study_hours_this_week / profile.weekly_goal) * 100;

  return (
    <motion.div
      className="min-h-screen w-full bg-background text-foreground flex flex-col p-4 sm:p-6"
      initial="hidden"
      animate="visible"
      variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.1 } } }}
    >
      {/* Header */}
      <motion.div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4 sm:gap-0" variants={cardVariants}>
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold flex items-center gap-2 text-foreground dark:text-white">
            <User className="w-7 h-7 text-primary" />My Profile
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground dark:text-gray-300">Manage your account and track your learning journey</p>
        </div>
        <div className="flex gap-2">
          <Button asChild variant="outline">
            <Link to="/gamification">Gamification</Link>
          </Button>
          <Button onClick={() => setIsEditing(!isEditing)} variant={isEditing ? "outline" : "default"} className="gap-2">
            {isEditing ? <><X className="w-4 h-4" /> Cancel</> : <><Edit3 className="w-4 h-4" /> Edit Profile</>}
          </Button>
        </div>
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
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }}>
                  <ProfileImageUpload
                    currentAvatarUrl={profile.avatar_url}
                    userName={profile.name || user?.email || "User"}
                    onUpload={uploadAvatar}
                  />
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    {isEditing ? (
                      <Input
                        id="name"
                        value={editData.name}
                        onChange={e => setEditData({ ...editData, name: e.target.value })}
                      />
                    ) : (
                      <p className="p-2 bg-gray-100 dark:bg-gray-700 rounded-md">{profile.name || "Not set"}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <p className="p-2 bg-gray-100 dark:bg-gray-700 rounded-md">{user?.email}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bio">Bio</Label>
                  {isEditing ? (
                    <Textarea
                      id="bio"
                      value={editData.bio}
                      onChange={e => setEditData({ ...editData, bio: e.target.value })}
                      rows={3}
                    />
                  ) : (
                    <p className="p-2 bg-gray-100 dark:bg-gray-700 rounded-md">{profile.bio || "No bio yet"}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="studyGoal">Current Study Goal</Label>
                  {isEditing ? (
                    <Input
                      id="studyGoal"
                      value={editData.study_goal}
                      onChange={e => setEditData({ ...editData, study_goal: e.target.value })}
                    />
                  ) : (
                    <p className="p-2 bg-gray-100 dark:bg-gray-700 rounded-md">{profile.study_goal || "No goal set"}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label>Preferred Subjects</Label>
                  <div className="flex flex-wrap gap-2">
                    {profile.preferred_subjects.map(s => (
                      <Badge key={s} variant="secondary" className="gap-1">
                        {s}
                        {isEditing && (
                          <X
                            className="w-3 h-3 cursor-pointer hover:text-destructive"
                            onClick={() => handleRemoveSubject(s)}
                          />
                        )}
                      </Badge>
                    ))}
                    {isEditing && (
                      <div className="flex gap-2 w-full mt-2">
                        <Input
                          placeholder="Add subject"
                          value={newSubject}
                          onChange={e => setNewSubject(e.target.value)}
                          onKeyPress={e => e.key === 'Enter' && handleAddSubject()}
                        />
                        <Button variant="outline" size="sm" onClick={handleAddSubject}>
                          <Plus className="w-4 h-4" />
                        </Button>
                      </div>
                    )}
                  </div>
                </div>

                {isEditing && (
                  <div className="space-y-2">
                    <Label htmlFor="weeklyGoal">Weekly Study Goal (hours)</Label>
                    <Input
                      id="weeklyGoal"
                      type="number"
                      value={editData.weekly_goal}
                      onChange={e => setEditData({ ...editData, weekly_goal: parseInt(e.target.value) || 30 })}
                    />
                  </div>
                )}

                {isEditing && (
                  <div className="flex flex-wrap gap-2 pt-4">
                    <Button onClick={handleSave} className="gap-2">
                      <Save className="w-4 h-4" /> Save Changes
                    </Button>
                    <Button variant="outline" onClick={handleCancel}>Cancel</Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </motion.div>

        {/* Stats Column */}
        <motion.div className="space-y-6" variants={cardVariants}>
          {/* Level & XP */}
          <div className="relative">
            <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-indigo-200 via-purple-200 to-pink-200 opacity-10 dark:opacity-30 blur-3xl pointer-events-none"></div>
            <Card className="relative bg-white dark:bg-gray-800/80 backdrop-blur-md shadow-lg border border-gray-200 dark:border-gray-700 hover:scale-105 transition-transform duration-500 ease-in-out">
              <CardHeader><CardTitle className="text-lg">Level & XP</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <XPProgressBar
                  totalXp={stats.total_xp ?? 0}
                  currentLevel={stats.current_level ?? 1}
                  xpToNextLevel={stats.xp_to_next_level ?? 100}
                />
              </CardContent>
            </Card>
          </div>

          {/* Study Statistics */}
          <div className="relative">
            <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-green-200 via-green-300 to-blue-300 opacity-10 dark:opacity-30 blur-3xl pointer-events-none"></div>
            <Card className="relative bg-white dark:bg-gray-800/80 backdrop-blur-md shadow-lg border border-gray-200 dark:border-gray-700 hover:scale-105 transition-transform duration-500 ease-in-out">
              <CardHeader><CardTitle className="text-lg">Study Statistics</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                {statsDisplay.map((s, i) => (
                  <motion.div
                    key={s.label}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.2, duration: 0.8, ease: easeInOut }}
                    className="flex items-center justify-between"
                  >
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
                    <span>{stats.study_hours_this_week}/{profile.weekly_goal} hrs</span>
                  </div>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 1, ease: easeInOut }}
                  >
                    <Progress value={weeklyProgress} className="h-2" />
                  </motion.div>
                </div>
                <p className="text-xs text-muted-foreground dark:text-gray-300">
                  {Math.max(0, profile.weekly_goal - stats.study_hours_this_week)} hours remaining this week
                </p>
              </CardContent>
            </Card>
          </div>
        </motion.div>
      </div>

      {/* Achievements */}
      <div className="relative mt-6">
        <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-yellow-200 via-pink-200 to-purple-200 opacity-10 dark:opacity-30 blur-3xl pointer-events-none"></div>
        <Card className="relative bg-white dark:bg-gray-800/80 backdrop-blur-md shadow-lg border border-gray-200 dark:border-gray-700 hover:scale-105 transition-transform duration-500 ease-in-out">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="w-5 h-5 text-primary" />Achievements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {achievements.map((a, i) => {
                const IconComponent = iconMap[a.icon] || Award;
                return (
                  <motion.div
                    key={a.id}
                    custom={i}
                    initial="hidden"
                    animate="visible"
                    variants={achievementVariants}
                    className={`p-4 rounded-lg border transition-all ${a.earned
                        ? 'bg-primary/5 border-primary/20 dark:ring-2 dark:ring-primary/50 dark:shadow-lg'
                        : 'bg-gray-100 dark:bg-gray-700/50 border-gray-200 dark:border-gray-600 opacity-60'
                      }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-full ${a.earned
                          ? 'bg-primary text-primary-foreground dark:bg-primary dark:text-white'
                          : 'bg-gray-200 dark:bg-gray-600 text-gray-500'
                        }`}>
                        <IconComponent className="w-4 h-4" />
                      </div>
                      <div className="space-y-1 flex-1">
                        <h4 className="font-medium text-sm">{a.title}</h4>
                        <p className="text-xs text-muted-foreground dark:text-gray-300">{a.description}</p>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
};
