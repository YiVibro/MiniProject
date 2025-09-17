import { useState } from "react";
import { useAuth } from "../store/AuthContext.tsx";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { supabase } from "../lib/supabaseClient";

interface GoogleUser {
  name: string;
  email: string;
  picture: string;
}

const Login = () => {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false); // ✅ track login/signup mode

  // ✅ Supabase Google OAuth flow
  const googleAuth = async () => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            // Google doesn’t fully separate login/signup,
            // but "consent" forces asking permissions again on signup
            prompt: isSignUp ? "consent" : "select_account",
          },
        },
      });

      if (error) {
        console.error("Google auth failed:", error.message);
      }
    } catch (err) {
      console.error("Unexpected Google auth error:", err);
    }
  };

  // Email/password login or signup (stub for now)
  const handleEmailAuth = (e: React.FormEvent) => {
    e.preventDefault();
    console.log(isSignUp ? "Signup" : "Login", { email, password });
    // TODO: Replace with backend auth call
    login({ name: "User", email, picture: "" });
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-green-900 via-emerald-800 to-black relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute w-80 h-80 bg-green-500/20 rounded-full blur-3xl top-10 left-10 animate-pulse"></div>
      <div className="absolute w-80 h-80 bg-emerald-400/20 rounded-full blur-3xl bottom-10 right-10 animate-pulse"></div>

      {/* Auth card */}
      <div className="w-full max-w-md bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 text-center border border-white/20 relative z-10">
        {/* Title */}
        <h1 className="text-4xl font-extrabold bg-gradient-to-r from-green-400 to-emerald-300 bg-clip-text text-transparent mb-3">
          StudySpark
        </h1>
        <p className="text-gray-200 mb-6">
          {isSignUp ? "Create your account" : "Sign in to continue your journey"}
        </p>

        {/* Email form */}
        <form onSubmit={handleEmailAuth} className="space-y-4">
          <Input
            type="email"
            placeholder="Email"
            className="bg-white/10 border border-white/30 text-white placeholder-gray-300 rounded-xl"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            type="password"
            placeholder="Password"
            className="bg-white/10 border border-white/30 text-white placeholder-gray-300 rounded-xl"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button
            type="submit"
            className="w-full rounded-xl bg-gradient-to-r from-green-500 to-emerald-500 hover:opacity-90 text-white font-semibold py-2 shadow-lg transition-all duration-300"
          >
            {isSignUp ? "Sign Up" : "Sign In"}
          </Button>
        </form>
          

        {/* Divider */}
        <div className="flex items-center my-6">
          <div className="flex-grow h-px bg-white/20"></div>
          <span className="px-3 text-sm text-gray-400">or</span>
          <div className="flex-grow h-px bg-white/20"></div>
        </div>

        {/* ✅ Google auth */}
        <Button
  onClick={googleAuth}
  className="w-full flex items-center justify-center gap-2 rounded-xl bg-white/10 hover:bg-white/20 text-white font-medium py-2 border border-white/30 shadow-lg transition-all duration-300"
>
  <img
    src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
    alt="Google"
    className="w-5 h-5"
  />
  {isSignUp ? "Sign up with Google" : "Sign in with Google"}
</Button>

         
        {/* Footer toggle */}
        <p className="mt-6 text-sm text-gray-100">
          {isSignUp ? "Already have an account?" : "Don’t have an account?"}{" "}
          <button type="button"
            onClick={() => setIsSignUp(!isSignUp)}
            className="text-green-400 hover:underline cursor-pointer"
          >
            {isSignUp ? "Sign in" : "Sign up"}
          </button>
        </p>
      </div>
    </div>
  );
};

export default Login;
