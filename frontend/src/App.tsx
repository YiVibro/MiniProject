import { useState } from "react";
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

import { Dashboard } from "./components/Dashboard";
import { Navigation } from "./components/Navigation";
import { AuthProvider, useAuth } from "./store/AuthContext";

const queryClient = new QueryClient();

// ✅ Protected route wrapper
const RequireAuth = ({ children }: { children: React.ReactNode }) => {
  const { user, token } = useAuth();
  const location = useLocation();

  if (!user || !token) {
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

// ✅ Layout with Navigation and activeTab state
const Layout = ({ children }: { children: React.ReactNode }) => {
  const [activeTab, setActiveTab] = useState("dashboard");

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

                {/* OAuth callback */}
                <Route path="/auth/callback" element={<AuthCallback />} />

                {/* Protected Dashboard */}
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

                {/* Protected Editor */}
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
