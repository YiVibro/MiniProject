import { useState } from "react";
import { supabase } from "../lib/supabaseClient";
import { useNavigate } from "react-router-dom";

const Signup = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");
  const navigate = useNavigate();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg("");

    try {
      // 1. Sign up the user
      const { data: authData, error: authError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { full_name: name }, // Pass name to metadata
        },
      });

      if (authError) {
        setMsg(authError.message);
        return;
      }

      if (authData.user) {
        // 2. Insert the new user into the public.users table
        const { error: insertError } = await supabase.from('users').insert({
          id: authData.user.id, // Use the user's ID from auth
          email: email,
          name: name,
        });

        if (insertError) {
          setMsg(`Signup successful, but failed to create user profile: ${insertError.message}`);
          return;
        }

        setMsg("Signup successful! Please check your email to verify your account.");

        // Optional: redirect to login page after a few seconds
        setTimeout(() => navigate("/login"), 3000);
      }
    } catch (err: any) {
      setMsg(err.message || "Something went wrong");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-green-100 via-emerald-100 to-blue-50">
      <div className="bg-white/90 backdrop-blur-lg p-8 rounded-2xl shadow-lg w-80">
        <h1 className="text-2xl font-bold mb-4 text-center text-gray-800">Create Account</h1>

        <form onSubmit={handleSignup} className="flex flex-col gap-3">
          <input
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="border p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400"
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="border p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="border p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400"
            required
          />

          {msg && <p className="text-sm text-center text-gray-700">{msg}</p>}

          <button
            type="submit"
            className="bg-green-500 text-white py-2 rounded-xl font-semibold shadow hover:opacity-90 transition duration-200"
          >
            Sign Up
          </button>
        </form>

        <p className="text-sm text-gray-600 mt-4 text-center">
          Already have an account?{" "}
          <button
            onClick={() => navigate("/login")}
            className="text-green-500 hover:underline font-medium"
          >
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
};

export default Signup;
