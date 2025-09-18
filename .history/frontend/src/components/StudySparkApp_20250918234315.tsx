import { useState } from "react";
import { LandingPage } from "./LandingPage";
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
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  // Login callback
   const handleLogin = () => {
    setIsLoggedIn(true);
  };

  if (!isLoggedIn) {
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
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main>{renderContent()}</main>
    </div>
  );
};
