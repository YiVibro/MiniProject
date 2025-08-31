import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";
import { useAuth } from "../store/AuthContext.tsx";

interface GoogleUser {
  name: string;
  email: string;
  picture: string;
}

const Login = () => {
  const { login } = useAuth();

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-green-900 via-green-800 to-gray-900 text-white">
      <div className="w-full max-w-md bg-gray-800/70 backdrop-blur-lg rounded-2xl shadow-2xl p-8 text-center border border-green-700">
        {/* Logo / Title */}
        <h1 className="text-4xl font-extrabold text-green-400 mb-3">StudySpark</h1>
        <p className="text-gray-300 mb-6">Sign in to continue your journey</p>

        {/* Google OAuth Login */}
        <div className="flex justify-center">
          <GoogleLogin
            onSuccess={(response) => {
              if (response.credential) {
                const decoded: any = jwtDecode(response.credential);
                const user: GoogleUser = {
                  name: decoded.name,
                  email: decoded.email,
                  picture: decoded.picture,
                };
                login(user);
              }
            }}
            onError={() => {
              console.error("Login Failed");
            }}
          />
        </div>

        {/* Extra Note */}
        <p className="mt-6 text-sm text-gray-400">
          By logging in, you agree to our{" "}
          <span className="text-green-400 hover:underline cursor-pointer">
            Terms of Service
          </span>{" "}
          and{" "}
          <span className="text-green-400 hover:underline cursor-pointer">
            Privacy Policy
          </span>
        </p>
      </div>
    </div>
  );
};

export default Login;
