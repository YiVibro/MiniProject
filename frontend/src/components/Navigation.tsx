import { useState } from "react";
import { Button } from "@/components/ui/button";
import { BookOpen, Brain, Users, MessageCircle, BarChart3, LogOut, SunMoon, Menu, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import studysparkLogo from "@/assets/studyspark-logo.png";

interface NavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export const Navigation = ({ activeTab, onTabChange }: NavigationProps) => {
  const [isDark, setIsDark] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleTheme = () => {
    setIsDark(!isDark);
    if (!isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: BarChart3 },
    { id: "courses", label: "My Courses", icon: BookOpen },
    { id: "ai-chat", label: "AI Tutor", icon: Brain },
    { id: "notes", label: "Notes", icon: MessageCircle },
    { id: "workshops", label: "Workshops", icon: Users },
  ];

  return (
    <>
      <nav className="flex items-center justify-between px-4 sm:px-6 py-3 bg-white/80 dark:bg-black backdrop-blur-md border-b border-border shadow-sm dark:shadow-[0_2px_10px_rgba(0,0,0,0.4)] transition-colors sticky top-0 z-50">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <img src={studysparkLogo} alt="StudySpark AI" className="w-8 h-8" />
          <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            StudySpark AI
          </h1>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden sm:flex items-center gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <Button
                key={item.id}
                variant={isActive ? "default" : "ghost"}
                size="sm"
                onClick={() => onTabChange(item.id)}
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

        {/* Profile, Theme Toggle & Hamburger */}
        <div className="flex items-center gap-2">
          <Button
            variant={activeTab === "profile" ? "default" : "outline"}
            size="sm"
            className="rounded-full transition-all duration-200 hover:shadow-md text-foreground dark:text-foreground/90 hover:bg-muted/60 dark:hover:bg-muted/50"
            onClick={() => onTabChange("profile")}
          >
            Profile
          </Button>

          <Button
            variant="outline"
            size="sm"
            className="rounded-full transition-all duration-200 hover:shadow-md text-foreground dark:text-foreground/90 hover:bg-muted/60 dark:hover:bg-muted/50"
            onClick={toggleTheme}
          >
            <SunMoon className="w-4 h-4" />
          </Button>

          {/* Mobile Hamburger */}
          <Button
            variant="outline"
            size="sm"
            className="sm:hidden rounded-full transition-all duration-200 text-foreground dark:text-gray-200 hover:bg-muted/60 dark:hover:bg-gray-800"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
        </div>
      </nav>

      {/* Animated Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="sm:hidden overflow-hidden bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border-b border-border shadow-md px-4 py-2 space-y-2 z-40"
          >
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <Button
                  key={item.id}
                  variant={isActive ? "default" : "ghost"}
                  size="sm"
                  className="w-full justify-start gap-2 rounded-lg text-foreground dark:text-gray-200 hover:bg-muted/60 dark:hover:bg-gray-800"
                  onClick={() => {
                    onTabChange(item.id);
                    setIsMobileMenuOpen(false);
                  }}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Logout Button */}
      <Button
        size="lg"
        className="fixed bottom-6 right-6 z-50 rounded-full shadow-lg bg-blue-500 text-white dark:bg-blue-600 dark:text-white hover:bg-blue-600 dark:hover:bg-blue-700 transition-colors duration-200"
        asChild
      >
        <a href="/">
          <LogOut className="w-5 h-5 mr-2" />
          Logout
        </a>
      </Button>
    </>
  );
};
