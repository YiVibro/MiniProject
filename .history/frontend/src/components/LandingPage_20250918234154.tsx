import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Brain, BookOpen, Target, TrendingUp, Sparkles, Loader2, Moon, Sun, Mail } from "lucide-react";
import studysparkLogo from "@/assets/studyspark-logo.png";
import { useTheme } from "@/theme";
import { FcGoogle } from "react-icons/fc";
import { motion } from "framer-motion";
import { supabase } from "../lib/supabaseClient";
import { Menu,X } from "lucide-react"; 
import { useAuth } from "../store/AuthContext.tsx";
import { useNavigate } from "react-router-dom";

interface LandingPageProps {
  onLogin: () => void;
}

export const LandingPage = ({ onLogin }: LandingPageProps) => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const { dark, toggle } = useTheme();
  const [highlightAuth, setHighlightAuth] = useState(false);
  const authCardRef = useRef<HTMLDivElement>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { login }= useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [errors, setErrors] = useState<{ email?: string; password?: string; name?: string }>({});

  // Features
  const features = [
    { icon: Brain, title: "AI-Powered Learning", description: "Get personalized study plans and instant answers from our advanced AI tutor" },
    { icon: Target, title: "Goal Tracking", description: "Set learning objectives and track your progress with detailed analytics" },
    { icon: BookOpen, title: "Smart Notes", description: "AI-generated summaries and personal note-taking in one unified system" },
    { icon: TrendingUp, title: "Progress Analytics", description: "Visualize your learning journey with comprehensive progress tracking" },
    { icon: Sparkles, title: "Interactive Lessons", description: "Engage with interactive lessons designed for better concept retention" },
    { icon: Mail, title: "Instant Q&A", description: "Ask questions and get immediate AI-generated answers to clarify doubts" },
    { icon: Loader2, title: "Real-Time Feedback", description: "Receive instant feedback on quizzes and assignments to improve learning outcomes" },
    { icon: Sparkles, title: "Gamified Learning", description: "Earn badges, points, and rewards as you progress through AI-powered modules" },
  ];

  // Scroll helper
  const handleScrollTo = (id: string) => {
  const el = document.getElementById(id);
  if (el) {
    const header = document.querySelector('header');
    const headerHeight = header ? header.offsetHeight : 0;

    const elementPosition = el.getBoundingClientRect().top + window.scrollY;
    const offsetPosition = elementPosition - headerHeight - 20; // Added a little extra for spacing
    
    // Scroll to the new position
    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
  }
};

  // Click outside auth card
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (authCardRef.current && !authCardRef.current.contains(event.target as Node)) {
        setHighlightAuth(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Form validation + submit
  const handleAuth = () => {
    const newErrors: typeof errors = {};
    if (!email.includes("@")) newErrors.email = "Enter a valid email";
    if (password.length < 6) newErrors.password = "Password must be at least 6 characters";
    if (!isLogin && name.trim() === "") newErrors.name = "Name is required";
    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      setLoading(true);
      setTimeout(() => {
        setLoading(false);
        onLogin();
      }, 1500);
    }
  };
  // OAuth
  const handleOAuth = async (provider: "google") => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: { prompt: isLogin ? "select_account" : "consent" },
        },
      });
      if (error) console.error("Google OAuth error:", error.message);
    } catch (err) {
      console.error("Unexpected OAuth error:", err);
    }
  };

  // Motion variants
  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.6 } } };
  const fadeIn = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { duration: 0.8 } } };

  return (
    <div className={`min-h-screen flex flex-col transition-colors duration-500 relative overflow-hidden ${dark ? "bg-[#121212]" : "bg-gray-50"}`}>
      {/* Header */}
      <header className="fixed top-0 w-full z-50 px-6 py-4 flex items-center justify-between backdrop-blur-md bg-opacity-60 bg-white dark:bg-[#1E1E1E]">
        <div className="flex items-center gap-2">
          <img src={studysparkLogo} alt="StudySpark AI" className="w-10 h-10" />
          <h1 className={`text-2xl font-bold ${dark ? "text-white" : "text-gray-900"}`}>StudySpark AI</h1>
        </div>
         
        {/* Desktop Nav */}
        <div className="hidden lg:flex items-center gap-4">
          <div className="flex flex-wrap items-center gap-4 md:gap-6 mr-2 md:mr-4">
            <button className={`${dark ? "text-gray-200" : "text-gray-800"} hover:underline font-medium`} onClick={() => handleScrollTo("about")}>About</button>
            <button className={`${dark ? "text-gray-200" : "text-gray-800"} hover:underline font-medium`} onClick={() => handleScrollTo("features")}>Features</button>
            <button className={`${dark ? "text-gray-200" : "text-gray-800"} hover:underline font-medium`} onClick={() => handleScrollTo("contact")}>Contact</button>
          </div>
          <Button
            variant="ghost"
            className={`${dark ? "text-gray-200 border-gray-400" : "text-gray-800 border-gray-700"} hover:bg-white/10 rounded-lg`}
            onClick={toggle}
            aria-label="Toggle theme"
          >
            {dark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </Button>
        </div>

        {/* Mobile Navigation (lg:hidden) */}
        <div className="lg:hidden flex items-center gap-4">
          <Button
            variant="ghost"
            className={`${dark ? "text-gray-200 border-gray-400" : "text-gray-800 border-gray-700"} hover:bg-white/10 rounded-lg`}
            onClick={toggle}
            aria-label="Toggle theme"
          >
            {dark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </Button>
          <Button
            variant="ghost"
            className={`${dark ? "text-gray-200" : "text-gray-800"}`}
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle mobile menu"
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </Button>
        </div>
      </header>

      {/* Mobile Menu Content */}
      <div className={`fixed top-0 right-0 z-40 h-full w-64 transition-transform transform duration-300 ease-in-out ${isMobileMenuOpen ? "translate-x-0" : "translate-x-full"} ${dark ? "bg-gray-900" : "bg-white"} shadow-xl lg:hidden`}>
        <div className="flex flex-col items-start gap-8 pt-20 px-6">
          <button className={`text-xl font-bold ${dark ? "text-gray-200" : "text-gray-800"} hover:underline`} onClick={() => { handleScrollTo("about"); setIsMobileMenuOpen(false); }}>About</button>
          <button className={`text-xl font-bold ${dark ? "text-gray-200" : "text-gray-800"} hover:underline`} onClick={() => { handleScrollTo("features"); setIsMobileMenuOpen(false); }}>Features</button>
          <button className={`text-xl font-bold ${dark ? "text-gray-200" : "text-gray-800"} hover:underline`} onClick={() => { handleScrollTo("contact"); setIsMobileMenuOpen(false); }}>Contact</button>
        </div>
      </div>

      {/* Main */}
      <main className="flex-grow w-full px-6 py-12 max-w-[1400px] mx-auto pt-[64px]">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center px-4 md:px-6" id="about">
          {/* Hero Section */}
          <motion.div className={`${dark ? "text-white" : "text-gray-900"} space-y-8`} initial="hidden" animate="visible" variants={fadeUp}>
            <div className="space-y-4">
              <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold leading-tight">
                Your AI Study <span className={dark ? "text-[#1FB6FF]" : "text-blue-600"}>Companion</span>
              </h2>
              <p className={`${dark ? "text-gray-300" : "text-gray-700"} text-lg sm:text-xl leading-relaxed`}>
                Transform your learning with personalized AI tutoring, smart goal tracking, and intelligent progress analytics. Begin your journey to academic excellence today.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row flex-wrap gap-4 justify-center sm:justify-start">
              <Button
                variant="hero"
                size="lg"
                className={`${dark ? "bg-[#1FB6FF] text-white hover:bg-[#0FA3E6]" : "bg-blue-600 text-white hover:bg-blue-500"} gap-2 shadow-lg`}
                onClick={() => {
                  setHighlightAuth(true);
                  const authCardEl = document.getElementById("auth-card");
                  if (authCardEl) {
                    const headerOffset = 80;
                    const elementPosition = authCardEl.getBoundingClientRect().top + window.scrollY;
                    const offsetPosition = elementPosition - headerOffset;
                    window.scrollTo({ top: offsetPosition, behavior: "smooth" });
                  }
                }}
              >
                <Sparkles className="w-5 h-5" /> Start Learning Free
              </Button>
            </div>
          </motion.div>

          {/* Auth Card */}
          <motion.div className="relative w-full max-w-md mx-auto mt-12" initial="hidden" animate="visible" variants={fadeUp}>
            <Card
              id="auth-card"
              ref={authCardRef}
              className={`relative z-20 rounded-xl shadow-2xl p-6 sm:p-8 transform transition-all duration-700
                ${dark ? "bg-[#1E1E1E] text-white border-gray-700" : "bg-white text-gray-900 border-gray-200"}
                ${highlightAuth ? "scale-105 ring-4 ring-[#1FB6FF]" : ""}
                hover:scale-105 hover:-translate-y-2`}
            >
              <CardHeader className="text-center space-y-2">
                <CardTitle className="text-2xl">{isLogin ? "Welcome Back!" : "Join StudySpark AI"}</CardTitle>
                <CardDescription>{isLogin ? "Sign in to continue your learning journey" : "Start your personalized learning experience"}</CardDescription>
              </CardHeader>

              <CardContent className="space-y-4">
                {!isLogin && (
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    <Input
                      id="name"
                      placeholder="Enter your full name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className={`${dark ? "bg-gray-800 text-white placeholder-gray-400 border-gray-600" : "bg-gray-100 text-gray-900 placeholder-gray-400 border-gray-300"}`}
                    />
                    {errors.name && <p className="text-red-500 text-sm">{errors.name}</p>}
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className={`${dark ? "bg-gray-800 text-white placeholder-gray-400 border-gray-600" : "bg-gray-100 text-gray-900 placeholder-gray-400 border-gray-300"}`}
                  />
                  {errors.email && <p className="text-red-500 text-sm">{errors.email}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className={`${dark ? "bg-gray-800 text-white placeholder-gray-400 border-gray-600" : "bg-gray-100 text-gray-900 placeholder-gray-400 border-gray-300"}`}
                  />
                  {errors.password && <p className="text-red-500 text-sm">{errors.password}</p>}
                </div>

                <div className="flex justify-center">
                  <Button
                    className={`${dark ? "bg-[#1FB6FF] text-white hover:bg-[#0FA3E6]" : "bg-blue-600 text-white hover:bg-blue-500"} mt-4 w-auto py-2 px-4 rounded-lg font-medium`}
                    onClick={handleAuth}
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : isLogin ? "Sign In" : "Create Account"}
                  </Button>
                </div>

                <div className="flex items-center my-4">
                  <hr className="flex-grow border-gray-300 dark:border-gray-600" />
                  <span className="mx-2 text-gray-500 dark:text-gray-400">OR</span>
                  <hr className="flex-grow border-gray-300 dark:border-gray-600" />
                </div>

                <div className="flex flex-col gap-3 mt-4">
                  <Button
                    className={`${dark ? "bg-[#1FB6FF] text-white hover:bg-[#0FA3E6]" : "bg-blue-600 text-white hover:bg-blue-500"} flex items-center justify-center gap-2 w-auto py-2 px-4 rounded-lg font-medium`}
                    onClick={() => handleOAuth("google")}
                  >
                    <FcGoogle className="w-5 h-5" />
                    {isLogin ? "Sign in with Google" : "Sign up with Google"}
                  </Button>
                </div>

                <div className="text-center text-sm mt-2">
                  {isLogin ? "Don't have an account? " : "Already have an account? "}
                  <button className="text-blue-600 hover:underline font-medium" onClick={() => setIsLogin(!isLogin)}>
                    {isLogin ? "Sign up" : "Sign in"}
                  </button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Features Section */}
        <motion.div id="features" className="mt-20 text-center pt-[80px]" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}>
          <h3 className={`text-3xl font-bold mb-4 ${dark ? "text-white" : "text-gray-900"}`}>Why Choose StudySpark AI?</h3>
          <p className={`${dark ? "text-gray-300" : "text-gray-700"} mb-12 text-lg max-w-3xl mx-auto`}>
            Discover the features that make learning more effective and engaging
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {features.map(({ icon: Icon, title, description }, idx) => (
              <motion.div key={title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1, duration: 0.5 }}>
                <Card className={`${dark ? "bg-gray-900 border-gray-700 text-white" : "bg-white/10 border-gray-200 text-gray-900"} rounded-xl shadow-[0_0_40px_rgba(129,140,300,0.3)] hover:scale-105 transition-transform duration-300`}>
                  <CardContent className="p-6 text-center space-y-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-blue-400 rounded-lg flex items-center justify-center mx-auto shadow-md">
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h4 className="font-semibold text-lg">{title}</h4>
                    <p className={`${dark ? "text-gray-300" : "text-gray-700"} text-sm`}>{description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </main>

      {/* Footer */}
      <motion.footer className={`${dark ? "text-gray-300" : "text-gray-700"} py-8 px-4 sm:px-6 text-center`} initial="hidden" animate="visible" variants={fadeIn}>
        <div className="flex flex-col items-center gap-4 pt-[80px]" id="contact">
          <div className="text-sm">&copy; {new Date().getFullYear()} StudySpark AI. All rights reserved.</div>
        </div>
      </motion.footer>
    </div>
  );
};