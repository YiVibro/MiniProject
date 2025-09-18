import { Button } from "@/components/ui/button";
import { BookOpen, Brain, Users, MessageCircle, BarChart3, LogOut, SunMoon, Menu, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import studysparkLogo from "@/assets/studyspark-logo.png";
import { useState } from "react";
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
    { id: "dashboard", label: "Dashboard", icon: BarChart3 },
    { id: "courses", label: "My Courses", icon: BookOpen },
    { id: "ai-chat", label: "AI Tutor", icon: Brain },
    { id: "notes", label: "Notes", icon: MessageCircle },
    { id: "workshops", label: "Workshops", icon: Users },
  ];

  const toggleTheme = () => {
    setIsDark(!isDark);
    if (!isDark) document.documentElement.classList.add("dark");
    else document.documentElement.classList.remove("dark");
  };

  const handleTabClick = (tabId: string) => {
    onTabChange(tabId);
    setIsMobileMenuOpen(false);
  };

  const handleLogout = async () => {
    await logout();
    se
    navigate("/");
  };

  return (
    <>
      <nav className="flex items-center justify-between px-4 sm:px-6 py-3 bg-white/80 dark:bg-black backdrop-blur-md border-b shadow-sm sticky top-0 z-50">
        {/* Logo */}
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
                onClick={() => handleTabClick(item.id)}
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
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={toggleTheme} className="rounded-full">
            <SunMoon className="w-4 h-4" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => handleTabClick("profile")}
            className="rounded-full hidden sm:flex"
          >
            Profile
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleLogout} // use new handler
            className="rounded-full hidden sm:flex"
          >
            <LogOut className="w-4 h-4" />
          </Button>

          {/* Mobile hamburger */}
          <Button
            variant="outline"
            size="sm"
            className="sm:hidden rounded-full"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
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
                  onClick={() => handleTabClick(item.id)}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Button>
              );
            })}

            {/* Profile & Logout */}
            <Button
              size="sm"
              className="w-full justify-start gap-2 rounded-lg"
              onClick={() => handleTabClick("profile")}
            >
              Profile
            </Button>

            <Button
              size="sm"
              className="w-full justify-start gap-2 rounded-lg"
              onClick={handleLogout} // redirect works on mobile too
            >
              <LogOut className="w-4 h-4" /> Logout
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
