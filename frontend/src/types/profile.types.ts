// TypeScript type definitions for user profile, stats, and achievements

export interface UserProfile {
    user_id: string;
    name: string;
    bio: string;
    study_goal: string;
    preferred_subjects: string[];
    weekly_goal: number;
    avatar_url: string | null;
    created_at?: string;
    updated_at?: string;
}

export interface UserProfileUpdate {
    name?: string;
    bio?: string;
    study_goal?: string;
    preferred_subjects?: string[];
    weekly_goal?: number;
    avatar_url?: string | null;
}

export interface UserStats {
    user_id: string;
    total_study_hours: number;
    courses_completed: number;
    current_streak: number;
    longest_streak: number;
    ai_interactions: number;
    study_hours_this_week: number;
    last_activity_date: string | null;
    total_xp?: number;
    current_level?: number;
    xp_to_next_level?: number;
    total_points?: number;
}

export interface Achievement {
    id: string;
    title: string;
    description: string;
    icon: string;
    earned: boolean;
    progress: number;
    earned_at: string | null;
}

export interface ProfileData {
    profile: UserProfile | null;
    stats: UserStats | null;
    achievements: Achievement[];
    loading: boolean;
    error: string | null;
}
