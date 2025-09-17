import { useState } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import TextEditor from "./pages/TextEditor";
import { ThemeProvider } from "./theme";
import { Dashboard } from "./components/Dashboard";
import { Navigation } from "./components/Navigation";
import AuthCallback from "./pages/AuthCallback";
import { AuthProvider } from "./store/AuthContext"; // ✅ import your provider

const queryClient = new QueryClient();

// ✅ Wrap dashboard and other protected pages in Layout
const Layout = ({ children }: { children: React.ReactNode }) => {
  const [activeTab, setActiveTab] = useState("dashboard");

  return (
    <div className="min-h-screen flex flex-col">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="flex-1">{children}</main>
    </div>
  );
};

const App = () => (
  <ThemeProvider>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <AuthProvider> {/* ✅ wrap here */}
          <BrowserRouter>
            <Routes>
              {/* Landing / Index page */}
              <Route path="/" element={<Index />} />

              {/* Dashboard wrapped in Layout with Navigation */}
              <Route
                path="/dashboard"
                element={
                  <Layout>
                    <Dashboard />
                  </Layout>
                }
              />

              {/* Editor page */}
              <Route path="/editor" element={<TextEditor />} />

              {/* OAuth callback */}
              <Route path="/auth/callback" element={<AuthCallback />} />

              {/* Catch-all */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </TooltipProvider>
    </QueryClientProvider>
  </ThemeProvider>
);

export default App;
