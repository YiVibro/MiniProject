import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { BookOpen, Brain, Users, MessageCircle, BarChart3, LogOut, Sun, Moon, Menu, X } from "lucide-react";
import { useNavigate } from "react-router-dom";
import studysparkLogo from "@/assets/studyspark-logo.png";
import { useAuth } from "../store/AuthContext";

interface NavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export const Navigation = ({ activeTab, onTabChange }: NavigationProps) => {
  const [isDark, setIsDark] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const { logout } = useAuth();
  const navigate = useNavigate();

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: BarChart3, path: "/dashboard" },
    { id: "courses", label: "My Courses", icon: BookOpen, path: "/courses" },
    { id: "ai-chat", label: "AI Tutor", icon: Brain, path: "/ai-chat" },
    { id: "notes", label: "Notes", icon: MessageCircle, path: "/notes" },
    { id: "workshops", label: "Workshops", icon: Users, path: "/workshops" },
  ];

  // Initialize theme from localStorage or system preference
  useEffect(() => {
    const storedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

    if (storedTheme === "dark" || (!storedTheme && prefersDark)) {
      document.documentElement.classList.add("dark");
      setIsDark(true);
    } else {
      document.documentElement.classList.remove("dark");
      setIsDark(false);
    }
  }, []);

  const toggleTheme = () => {
    if (isDark) {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
      setIsDark(false);
    } else {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
      setIsDark(true);
    }
  };

  const handleTabClick = (tabId: string, path?: string) => {
    onTabChange(tabId);
    setIsMobileMenuOpen(false);
    if (path) navigate(path);
  };

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <>
      <nav className="flex items-center justify-between px-4 sm:px-6 py-3 bg-white/80 dark:bg-black backdrop-blur-md border-b shadow-sm sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <img src={studysparkLogo} alt="StudySpark AI" className="w-8 h-8" />
          <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            StudySpark AI
          </h1>
        </div>

        {/* Desktop nav */}
        <div className="hidden sm:flex items-center gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <Button
                key={item.id}
                variant={isActive ? "default" : "ghost"}
                size="sm"
                onClick={() => handleTabClick(item.id, item.path)}
                className={`gap-2 rounded-full px-4 transition-all duration-200 ${
                  isActive
                    ? "shadow-md ring-2 ring-primary/50 dark:ring-primary/60 text-foreground"
                    : "text-foreground/70 dark:text-gray-300 hover:text-foreground hover:bg-muted dark:hover:bg-gray-800"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{item.label}</span>
              </Button>
            );
          })}
        </div>

        {/* Profile, Theme, Hamburger */}
        <div className="flex items-center gap-2 text-gray-900 dark:text-gray-100">
          {/* Theme toggle */}
          <Button variant="outline" size="sm" onClick={toggleTheme} className="rounded-full">
            {isDark ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => handleTabClick("profile", "/profile")}
            className="rounded-full hidden sm:flex"
          >
            Profile
          </Button>

          <Button variant="outline" size="sm" onClick={handleLogout} className="rounded-full hidden sm:flex">
            <LogOut className="w-4 h-4" />
          </Button>

          <Button variant="outline" size="sm" className="sm:hidden rounded-full" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
        </div>
      </nav>

      {/* Mobile menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="sm:hidden overflow-hidden bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border-b shadow-md px-4 py-2 space-y-2"
          >
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <Button
                  key={item.id}
                  variant={isActive ? "default" : "ghost"}
                  size="sm"
                  className="w-full justify-start gap-2 rounded-lg"
                  onClick={() => handleTabClick(item.id, item.path)}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Button>
              );
            })}

            <Button size="sm" className="w-full justify-start gap-2 rounded-lg" onClick={() => handleTabClick("profile", "/profile")}>
              Profile
            </Button>

            <Button size="sm" className="w-full justify-start gap-2 rounded-lg" onClick={handleLogout}>
              <LogOut className="w-4 h-4" /> Logout
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
