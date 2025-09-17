import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { supabase } from "../lib/supabaseClient";

interface User {
  name: string;
  email: string;
  picture?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (user: User, token?: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(JSON.parse(localStorage.getItem("user") || "null"));
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
  const [loading, setLoading] = useState(true);

  const login = (user: User, token?: string) => {
    setUser(user);
    if (token) {
      setToken(token);
      localStorage.setItem("token", token);
    }
    localStorage.setItem("user", JSON.stringify(user));
  };

  const logout = async () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    await supabase.auth.signOut();
  };

  useEffect(() => {
    const getSession = async () => {
      const { data } = await supabase.auth.getSession();
      if (data.session) {
        const sUser = data.session.user;
        const authUser: User = {
          name: sUser.user_metadata?.full_name || sUser.email!,
          email: sUser.email!,
          picture: sUser.user_metadata?.avatar_url,
        };
        setUser(authUser);
        setToken(data.session.access_token);
        localStorage.setItem("user", JSON.stringify(authUser));
        localStorage.setItem("token", data.session.access_token);
      }
      setLoading(false);
    };

    getSession();

    const { data: subscription } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        const sUser = session.user;
        const authUser: User = {
          name: sUser.user_metadata?.full_name || sUser.email!,
          email: sUser.email!,
          picture: sUser.user_metadata?.avatar_url,
        };
        setUser(authUser);
        setToken(session.access_token);
        localStorage.setItem("user", JSON.stringify(authUser));
        localStorage.setItem("token", session.access_token);
      } else {
        setUser(null);
        setToken(null);
        localStorage.removeItem("user");
        localStorage.removeItem("token");
      }
      setLoading(false);
    });

    return () => subscription?.subscription.unsubscribe();
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
