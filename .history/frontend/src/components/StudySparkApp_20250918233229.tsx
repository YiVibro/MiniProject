import { useState } from "react";
import { LandingPage } from "./LandingPage";
import { Navigation } from "./Navigation";
import { Dashboard } from "./Dashboard";
import { AIChatInterface } from "./AIChatInterface";
import { NotesSection } from "./NotesSection";
import { Workshops } from "./Workshops";
import { Profile } from "./Profile";
import { CoursesPage } from "./CoursesPage";
import { useAuth } from "../store/AuthContext";
import { supabase } from "../lib/supabaseClient";

export const StudySparkApp = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("dashboard");

  // Login callback
  const handleLogin = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    console.error("Login error:", error.message);
  } else {
    // redirect to dashboard
    window.location.href = "/dashboard";
  }
};

  // Show landing page if user is not logged in
  if (!user) {
    return <LandingPage onLogin={handleLogin} />;
  }

  // Render content based on active tab
  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <Dashboard />;
      case "courses":
        return <CoursesPage />;
      case "ai-chat":
        return <AIChatInterface />;
      case "notes":
        return <NotesSection />;
      case "workshops":
        return <Workshops />;
      case "profile":
        return <Profile />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <main>{renderContent()}</main>
    </div>
  );
};
