// src/pages/AuthCallback.tsx

import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../store/AuthContext";
import { supabase } from "../lib/supabaseClient";

const AuthCallback = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { hash, search } = useLocation();  // use hash and search

  const [status, setStatus] = useState("Finishing sign-in…");
  const [error, setError] = useState<string | null>(null);
  const [debug, setDebug] = useState<Record<string, unknown>>({});

  useEffect(() => {
    const finishAuth = async () => {
      try {
        console.debug("[AuthCallback] href:", window.location.href);
        console.debug("[AuthCallback] origin:", window.location.origin);
        const debugInfo: Record<string, unknown> = { href: window.location.href };

        // Helper: wait briefly for session changes
        const waitForSession = (timeoutMs = 6000) =>
          new Promise<import("@supabase/supabase-js").Session | null>((resolve) => {
            const startedAt = Date.now();
            const { data: subscription } = supabase.auth.onAuthStateChange((_event, session) => {
              if (session) {
                console.debug("[AuthCallback] onAuthStateChange session detected");
                subscription.subscription.unsubscribe();
                resolve(session);
              }
            });
            setTimeout(() => {
              console.debug("[AuthCallback] waitForSession timeout", { elapsedMs: Date.now() - startedAt });
              subscription.subscription.unsubscribe();
              resolve(null);
            }, timeoutMs);
          });

        // Handle PKCE code exchange (?code=...)
        const params = new URLSearchParams(search || window.location.search);
        const errorDescription = params.get("error_description");
        const code = params.get("code");

        if (errorDescription) {
          console.error("OAuth error:", errorDescription);
          setError(errorDescription);
          setStatus("Login failed. Redirecting…");
          setTimeout(() => navigate("/"), 2000);
          return;
        }

        if (code) {
          setStatus("Signing you in…");
          console.debug("[AuthCallback] exchanging code for session");
          const { data: exData, error: exErr } = await supabase.auth.exchangeCodeForSession(code);
          if (exErr) {
            console.error("Code exchange failed:", exErr.message);
            setError(exErr.message);
            setStatus("Login failed. Redirecting…");
            setTimeout(() => navigate("/"), 2000);
            return;
          }

          if (exData?.session) {
            console.debug("[AuthCallback] code exchange returned session");
            const sUser = exData.session.user;
            login({
              name: sUser.user_metadata?.full_name || sUser.email!,
              email: sUser.email!,
              picture: sUser.user_metadata?.avatar_url,
            }, exData.session.access_token);

            setStatus("Login successful! Redirecting…");
            setTimeout(() => {
              window.location.href = "/dashboard";
            }, 1000);
            return;
          }

          // If no session in response, wait briefly for auth listener then try getSession
          console.debug("[AuthCallback] no session in exchange response, waiting for session event…");
          await waitForSession();
          const postEx = await supabase.auth.getSession();
          console.debug("[AuthCallback] post-exchange getSession:", { hasSession: !!postEx.data.session });
          if (postEx.data.session) {
            const sUser = postEx.data.session.user;
            login({
              name: sUser.user_metadata?.full_name || sUser.email!,
              email: sUser.email!,
              picture: sUser.user_metadata?.avatar_url,
            }, postEx.data.session.access_token);
            setStatus("Login successful! Redirecting…");
            setTimeout(() => {
              window.location.href = "/dashboard";
            }, 800);
            return;
          }
          debugInfo.postExchangeNoSession = true;
        }

        // If there is a hash (#access_token=...), let Supabase process it
        if (hash && hash.includes("access_token")) {
          // Supabase automatically detects hash fragment and stores session
          // On newer versions supabase-js might already handle it via authListener or getSession

          // Wait a moment for Supabase auth state to update
          const waitForUser = new Promise<void>((resolve) => {
            const { data: subscription } = supabase.auth.onAuthStateChange((_event, session) => {
              if (session) {
                resolve();
                subscription.subscription.unsubscribe();
              }
            });
          });

          await waitForUser;

          const { data: sessData, error: sessionError } = await supabase.auth.getSession();

          if (sessionError) {
            console.error("Session error after hash:", sessionError.message);
            setError(sessionError.message);
            setStatus("Login failed. Redirecting…");
            setTimeout(() => navigate("/"), 2000);
            return;
          }

          if (sessData.session) {
            console.debug("[AuthCallback] hash flow produced session");
            const sUser = sessData.session.user;
            login({
              name: sUser.user_metadata?.full_name || sUser.email!,
              email: sUser.email!,
              picture: sUser.user_metadata?.avatar_url,
            }, sessData.session.access_token);

            setStatus("Login successful! Redirecting…");
            setTimeout(() => {
              window.location.href = "/dashboard";
            }, 1000);
            return;
          }
          debugInfo.hashNoSession = true;
        }

        // Fallback: try getSession normally
        const { data, error } = await supabase.auth.getSession();
        if (error) {
          console.error("Auth error:", error.message);
          setError(error.message);
          setStatus("Login failed. Redirecting…");
          setTimeout(() => navigate("/"), 2000);
          return;
        }
        if (data.session) {
          console.debug("[AuthCallback] fallback getSession returned session");
          const sUser = data.session.user;
          login({
            name: sUser.user_metadata?.full_name || sUser.email!,
            email: sUser.email!,
            picture: sUser.user_metadata?.avatar_url,
          }, data.session.access_token);

          setStatus("Login successful! Redirecting…");
          setTimeout(() => {
            window.location.href = "/dashboard";
          }, 1000);
        } else {
          debugInfo.noSessionFinal = true;
          setDebug(debugInfo);
          console.debug("[AuthCallback] No session detected after all flows");
          setStatus("No active session. Redirecting…");
          setTimeout(() => navigate("/"), 2000);
        }
      } catch (err) {
        console.error("Unexpected error:", err);
        setError(err instanceof Error ? err.message : "An unexpected error occurred");
        setStatus("Unexpected error. Redirecting…");
        setTimeout(() => navigate("/"), 2000);
      }
    };

    finishAuth();
  }, [hash, search, login, navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-background text-foreground">
      <div className="text-center">
        <p className="text-lg font-medium">{status}</p>
        {error && (
          <p className="text-sm text-red-500 mt-2">
            Error: {error}
          </p>
        )}
        {import.meta.env.DEV && (
          <pre className="text-xs text-muted-foreground mt-3 text-left max-w-xl mx-auto break-all whitespace-pre-wrap">
            {JSON.stringify(debug, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
};

export default AuthCallback;
