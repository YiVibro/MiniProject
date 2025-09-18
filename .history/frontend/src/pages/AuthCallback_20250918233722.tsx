import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabaseClient";
import { useAuth } from "../store/AuthContext.tsx";

const AuthCallback = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // ✅ Fetch the session after redirect from Google
        const { data, error } = await supabase.auth.getSession();

        if (error) throw error;

        if (data.session) {
          const sUser = data.session.user;
          const authUser = {
            name: sUser.user_metadata?.full_name || sUser.email!,
            email: sUser.email!,
            picture: sUser.user_metadata?.avatar_url,
          };

          // ✅ Store in global auth context
          login(authUser, data.session.access_token);

          // ✅ Redirect to dashboard
          navigate("/dashboard", { replace: true });
        } else {
          // No session found
          navigate("/login", { replace: true });
        }
      } catch (err: any) {
        console.error("Auth callback error:", err.message);
        navigate("/login", { replace: true });
      }
    };

    handleCallback();
  }, [login, navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-green-900 via-emerald-800 to-black">
      <h2 className="text-white text-lg">Signing you in...</h2>
    </div>
  );
};

export default AuthCallback;
