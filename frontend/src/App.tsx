import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "./theme";

import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import TextEditor from "./pages/TextEditor";
import AuthCallback from "./pages/AuthCallback";
import Signup from "./pages/Signup";
import Login from "./pages/Login";

import { Dashboard } from "./components/Dashboard";
import { AIChatInterface } from "./components/AIChatInterface";
import { CoursesPage } from "./components/CoursesPage";
import { NotesSection } from "./components/NotesSection";
import { Workshops } from "./components/Workshops";
import { Profile } from "./components/Profile";
import { Navigation } from "./components/Navigation";
import { AuthProvider, useAuth } from "./store/AuthContext";
import CoursePage from "./pages/CoursePage";

const queryClient = new QueryClient();

// ✅ Protected route wrapper
const RequireAuth = ({ children }: { children: React.ReactNode }) => {
  const { user, ready } = useAuth();
  const location = useLocation();

  if (!ready) return null;

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

// ✅ Layout with Navigation and activeTab state
const Layout = ({ children }: { children: React.ReactNode }) => {
  const location = useLocation();
  const [activeTab, setActiveTab] = useState("dashboard");

  // Sync activeTab with current path
  useEffect(() => {
    switch (location.pathname) {
      case "/dashboard":
        setActiveTab("dashboard");
        break;
      case "/courses":
        setActiveTab("courses");
        break;
      case "/ai-chat":
        setActiveTab("ai-chat");
        break;
      case "/notes":
        setActiveTab("notes");
        break;
      case "/workshops":
        setActiveTab("workshops");
        break;
      case "/profile":
        setActiveTab("profile");
        break;
      default:
        setActiveTab("dashboard");
    }
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex flex-col">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="flex-1">{children}</main>
    </div>
  );
};

// ✅ App component
const App = () => {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <AuthProvider>
            <BrowserRouter>
              <Routes>
                {/* Landing page */}
                <Route path="/" element={<Index />} />

                {/* Login & Signup */}
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />

                {/* OAuth callback */}
                <Route path="/auth/callback" element={<AuthCallback />} />

                {/* Protected pages */}
                <Route
                  path="/course/:courseId"
                  element={
                    <RequireAuth>
                      <Layout>
                        <CoursePage />
                      </Layout>
                    </RequireAuth>
                  }
                />
                <Route
                  path="/dashboard"
                  element={
                    <RequireAuth>
                      <Layout>
                        <Dashboard />
                      </Layout>
                    </RequireAuth>
                  }
                />
                <Route
                  path="/courses"
                  element={
                    <RequireAuth>
                      <Layout>
                        <CoursesPage />
                      </Layout>
                    </RequireAuth>
                  }
                />
                <Route
                  path="/ai-chat"
                  element={
                    <RequireAuth>
                      <Layout>
                        <AIChatInterface />
                      </Layout>
                    </RequireAuth>
                  }
                />
                <Route
                  path="/notes"
                  element={
                    <RequireAuth>
                      <Layout>
                        <NotesSection />
                      </Layout>
                    </RequireAuth>
                  }
                />
                <Route
                  path="/workshops"
                  element={
                    <RequireAuth>
                      <Layout>
                        <Workshops />
                      </Layout>
                    </RequireAuth>
                  }
                />
                <Route
                  path="/profile"
                  element={
                    <RequireAuth>
                      <Layout>
                        <Profile />
                      </Layout>
                    </RequireAuth>
                  }
                />

                {/* Editor */}
                <Route
                  path="/editor"
                  element={
                    <RequireAuth>
                      <Layout>
                        <TextEditor />
                      </Layout>
                    </RequireAuth>
                  }
                />

                {/* Catch-all */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </BrowserRouter>
          </AuthProvider>
        </TooltipProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
};

export default App;
