import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { supabase } from "../lib/supabaseClient";
import { useAuth } from "../store/AuthContext";

const AuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { ready } = useAuth();
  const [status, setStatus] = useState("Finishing sign-in…");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const finishAuth = async () => {
      try {
        if (!ready) return;

        // 1️⃣ Check existing session
        const { data: { session } } = await supabase.auth.getSession();

        if (session?.user) {
          // Ensure metadata exists for first-time login
          const userMeta = session.user.user_metadata;
          if (!userMeta?.full_name) {
            await supabase.auth.updateUser({
              data: { full_name: session.user.email?.split("@")[0] || "User" },
            });
            console.debug("[AuthCallback] First-time Google login → metadata initialized");
          }

          setStatus("Login successful! Redirecting…");
          setTimeout(() => navigate("/dashboard"), 1000);
          return;
        }

        // 2️⃣ Parse OAuth parameters from URL (search or hash)
        const queryString = location.search || location.hash.replace("#", "?");
        const params = new URLSearchParams(queryString);
        const code = params.get("code");
        const access_token = params.get("access_token");
        const refresh_token = params.get("refresh_token");

        if (!code && !access_token) {
          console.debug("[AuthCallback] No auth code or access token in URL, redirecting…");
          setStatus("Redirecting…");
          setTimeout(() => navigate("/"), 1000);
          return;
        }

        // 3️⃣ Exchange code or set session
        let newSession;
        if (code) {
          const { data, error } = await supabase.auth.exchangeCodeForSession(code);
          if (error) throw error;
          newSession = data.session;
        } else if (access_token) {
          const { data, error } = await supabase.auth.setSession({
            access_token,
            refresh_token: refresh_token || undefined,
          });
          if (error) throw error;
          newSession = data.session;
        }

        // 4️⃣ Ensure metadata for first-time login
        if (newSession?.user) {
          const userMeta = newSession.user.user_metadata;
          if (!userMeta?.full_name) {
            await supabase.auth.updateUser({
              data: { full_name: newSession.user.email?.split("@")[0] || "User" },
            });
            console.debug("[AuthCallback] First-time Google login → metadata initialized");
          }

          setStatus("Login successful! Redirecting…");
          setTimeout(() => navigate("/dashboard"), 1000);
        } else {
          setStatus("No active session. Redirecting…");
          setTimeout(() => navigate("/"), 2000);
        }
      } catch (err) {
        console.error("[AuthCallback] Unexpected error:", err);
        setError(err instanceof Error ? err.message : "Unexpected error");
        setStatus("Unexpected error. Redirecting…");
        setTimeout(() => navigate("/"), 2000);
      }
    };

    finishAuth();
  }, [ready, location.search, location.hash, navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-background text-foreground">
      <div className="text-center">
        <p className="text-lg font-medium">{status}</p>
        {error && <p className="text-sm text-red-500 mt-2">Error: {error}</p>}
      </div>
    </div>
  );
};

export default AuthCallback;
