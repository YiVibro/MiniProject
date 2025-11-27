import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabaseClient";
import { useAuth } from "@/store/AuthContext";
import { UserProfile, UserStats, Achievement, ProfileData, UserProfileUpdate } from "@/types/profile.types";

export const useUserProfile = () => {
    const { user } = useAuth();
    const [profileData, setProfileData] = useState<ProfileData>({
        profile: null,
        stats: null,
        achievements: [],
        loading: true,
        error: null,
    });

    // Fetch profile data
    const fetchProfile = async () => {
        if (!user?.id) return;

        try {
            const { data, error } = await supabase
                .from("user_profiles")
                .select("*")
                .eq("user_id", user.id)
                .maybeSingle();

            if (error) {
                // Check if table doesn't exist
                if (error.message.includes("relation") || error.message.includes("does not exist")) {
                    setProfileData((prev) => ({
                        ...prev,
                        error: "Database tables not set up. Please run the migrations from PROFILE_SETUP.md"
                    }));
                    return;
                }
                throw error;
            }

            // If no profile exists, create a default one
            if (!data) {
                const defaultProfile = {
                    user_id: user.id,
                    name: user.email?.split('@')[0] || '',
                    bio: '',
                    study_goal: '',
                    preferred_subjects: [],
                    weekly_goal: 30,
                    avatar_url: null
                };

                const { data: newProfile, error: insertError } = await supabase
                    .from("user_profiles")
                    .insert(defaultProfile)
                    .select()
                    .single();

                if (insertError) throw insertError;
                setProfileData((prev) => ({ ...prev, profile: newProfile as UserProfile }));
            } else {
                setProfileData((prev) => ({ ...prev, profile: data as UserProfile }));
            }
        } catch (error: any) {
            console.error("Error fetching profile:", error);
            setProfileData((prev) => ({ ...prev, error: error.message }));
        }
    };

    // Fetch stats
    const fetchStats = async () => {
        if (!user?.id) return;

        try {
            const { data, error } = await supabase
                .from("user_stats")
                .select("*")
                .eq("user_id", user.id)
                .maybeSingle();

            if (error) {
                if (error.message.includes("relation") || error.message.includes("does not exist")) {
                    return; // Table doesn't exist, skip
                }
                throw error;
            }

            // If no stats exist, create default ones
            if (!data) {
                const defaultStats = {
                    user_id: user.id,
                    total_study_hours: 0,
                    courses_completed: 0,
                    current_streak: 0,
                    longest_streak: 0,
                    ai_interactions: 0,
                    study_hours_this_week: 0,
                    last_activity_date: null,
                    week_start_date: new Date().toISOString().split('T')[0]
                };

                const { data: newStats, error: insertError } = await supabase
                    .from("user_stats")
                    .insert(defaultStats)
                    .select()
                    .single();

                if (insertError) throw insertError;
                setProfileData((prev) => ({ ...prev, stats: newStats as UserStats }));
            } else {
                setProfileData((prev) => ({ ...prev, stats: data as UserStats }));
            }
        } catch (error: any) {
            console.error("Error fetching stats:", error);
            setProfileData((prev) => ({ ...prev, error: error.message }));
        }
    };

    // Fetch achievements
    const fetchAchievements = async () => {
        if (!user?.id) return;

        try {
            const { data, error } = await supabase
                .from("user_achievements")
                .select(`
          *,
          achievements (*)
        `)
                .eq("user_id", user.id);

            if (error) {
                if (error.message.includes("relation") || error.message.includes("does not exist")) {
                    setProfileData((prev) => ({ ...prev, achievements: [] }));
                    return; // Table doesn't exist, skip
                }
                throw error;
            }

            if (!data || data.length === 0) {
                setProfileData((prev) => ({ ...prev, achievements: [] }));
                return;
            }

            const achievements = data.map((item: any) => ({
                id: item.achievements.id,
                title: item.achievements.title,
                description: item.achievements.description,
                icon: item.achievements.icon,
                earned: item.earned,
                progress: item.progress,
                earned_at: item.earned_at,
            }));

            setProfileData((prev) => ({ ...prev, achievements }));
        } catch (error: any) {
            console.error("Error fetching achievements:", error);
            // Don't set error for achievements, just log it
            setProfileData((prev) => ({ ...prev, achievements: [] }));
        }
    };

    // Load all data on mount
    useEffect(() => {
        const loadData = async () => {
            if (!user?.id) {
                setProfileData({
                    profile: null,
                    stats: null,
                    achievements: [],
                    loading: false,
                    error: null,
                });
                return;
            }

            setProfileData((prev) => ({ ...prev, loading: true, error: null }));

            await Promise.all([fetchProfile(), fetchStats(), fetchAchievements()]);

            setProfileData((prev) => ({ ...prev, loading: false }));
        };

        loadData();
    }, [user?.id]);

    // Set up real-time subscriptions
    useEffect(() => {
        if (!user?.id) return;

        // Subscribe to profile changes
        const profileSubscription = supabase
            .channel("profile_changes")
            .on(
                "postgres_changes",
                {
                    event: "*",
                    schema: "public",
                    table: "user_profiles",
                    filter: `user_id=eq.${user.id}`,
                },
                (payload) => {
                    console.log("Profile changed:", payload);
                    if (payload.new) {
                        setProfileData((prev) => ({
                            ...prev,
                            profile: payload.new as UserProfile,
                        }));
                    }
                }
            )
            .subscribe();

        // Subscribe to stats changes
        const statsSubscription = supabase
            .channel("stats_changes")
            .on(
                "postgres_changes",
                {
                    event: "*",
                    schema: "public",
                    table: "user_stats",
                    filter: `user_id=eq.${user.id}`,
                },
                (payload) => {
                    console.log("Stats changed:", payload);
                    if (payload.new) {
                        setProfileData((prev) => ({
                            ...prev,
                            stats: payload.new as UserStats,
                        }));
                    }
                }
            )
            .subscribe();

        // Subscribe to achievements changes
        const achievementsSubscription = supabase
            .channel("achievements_changes")
            .on(
                "postgres_changes",
                {
                    event: "*",
                    schema: "public",
                    table: "user_achievements",
                    filter: `user_id=eq.${user.id}`,
                },
                () => {
                    console.log("Achievements changed, refetching...");
                    fetchAchievements();
                }
            )
            .subscribe();

        return () => {
            profileSubscription.unsubscribe();
            statsSubscription.unsubscribe();
            achievementsSubscription.unsubscribe();
        };
    }, [user?.id]);

    // Update profile
    const updateProfile = async (updates: UserProfileUpdate) => {
        if (!user?.id) return { success: false, error: "User not authenticated" };

        try {
            // Optimistic update
            setProfileData((prev) => ({
                ...prev,
                profile: prev.profile ? { ...prev.profile, ...updates } : null,
            }));

            const { data, error } = await supabase
                .from("user_profiles")
                .update(updates)
                .eq("user_id", user.id)
                .select()
                .single();

            if (error) throw error;

            setProfileData((prev) => ({ ...prev, profile: data as UserProfile }));
            return { success: true, data };
        } catch (error: any) {
            console.error("Error updating profile:", error);
            // Revert optimistic update
            await fetchProfile();
            return { success: false, error: error.message };
        }
    };

    // Upload avatar
    const uploadAvatar = async (file: File) => {
        if (!user?.id) return { success: false, error: "User not authenticated" };

        try {
            const fileExt = file.name.split(".").pop();
            const filePath = `avatars/${user.id}.${fileExt}`;

            // Upload to Supabase Storage
            const { error: uploadError } = await supabase.storage
                .from("profile-images")
                .upload(filePath, file, { upsert: true });

            if (uploadError) throw uploadError;

            // Get public URL
            const { data: urlData } = supabase.storage
                .from("profile-images")
                .getPublicUrl(filePath);

            const avatarUrl = urlData.publicUrl;

            // Update profile with new avatar URL
            const { error: updateError } = await supabase
                .from("user_profiles")
                .update({ avatar_url: avatarUrl })
                .eq("user_id", user.id);

            if (updateError) throw updateError;

            // Update local state
            setProfileData((prev) => ({
                ...prev,
                profile: prev.profile ? { ...prev.profile, avatar_url: avatarUrl } : null,
            }));

            return { success: true, url: avatarUrl };
        } catch (error: any) {
            console.error("Error uploading avatar:", error);
            return { success: false, error: error.message };
        }
    };

    // Add subject to preferred subjects
    const addSubject = async (subject: string) => {
        if (!profileData.profile) return;

        const currentSubjects = profileData.profile.preferred_subjects || [];
        if (currentSubjects.includes(subject)) return;

        const newSubjects = [...currentSubjects, subject];
        await updateProfile({ preferred_subjects: newSubjects });
    };

    // Remove subject from preferred subjects
    const removeSubject = async (subject: string) => {
        if (!profileData.profile) return;

        const currentSubjects = profileData.profile.preferred_subjects || [];
        const newSubjects = currentSubjects.filter((s) => s !== subject);
        await updateProfile({ preferred_subjects: newSubjects });
    };

    return {
        ...profileData,
        updateProfile,
        uploadAvatar,
        addSubject,
        removeSubject,
        refetch: async () => {
            setProfileData((prev) => ({ ...prev, loading: true }));
            await Promise.all([fetchProfile(), fetchStats(), fetchAchievements()]);
            setProfileData((prev) => ({ ...prev, loading: false }));
        },
    };
};
