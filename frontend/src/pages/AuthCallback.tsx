import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../store/AuthContext";
import { supabase } from "../lib/supabaseClient";

const AuthCallback = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { hash } = useLocation(); // Google returns access_token in hash
  const [status, setStatus] = useState("Finishing sign-in…");

  useEffect(() => {
    const finishAuth = async () => {
      try {
        // Supabase OAuth
        const { data: sessionData, error } = await supabase.auth.getSession();
        if (error) {
          setStatus("Login failed. Redirecting…");
          console.error(error);
          setTimeout(() => navigate("/"), 2000);
          return;
        }

        if (sessionData.session) {
          const sUser = sessionData.session.user;
          const authUser = {
            name: sUser.user_metadata?.full_name || sUser.email,
            email: sUser.email!,
            picture: sUser.user_metadata?.avatar_url,
          };

          login(authUser, sessionData.session.access_token);

          setStatus("Login successful! Redirecting…");
          setTimeout(() => navigate("/dashboard"), 1000);
        } else {
          setStatus("No active session. Redirecting…");
          setTimeout(() => navigate("/"), 2000);
        }
      } catch (err) {
        console.error("Unexpected error:", err);
        setStatus("Unexpected error. Redirecting…");
        setTimeout(() => navigate("/"), 2000);
      }
    };

    finishAuth();
  }, [hash, login, navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-background text-foreground">
      <p className="text-lg font-medium">{status}</p>
    </div>
  );
};

export default AuthCallback;
