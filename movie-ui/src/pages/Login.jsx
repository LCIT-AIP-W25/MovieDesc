import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AiFillEye, AiFillEyeInvisible } from "react-icons/ai";

const Login = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [toastMessage, setToastMessage] = useState("");
  const [toast, setToast] = useState({ message: "", type: "" });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");

      // ✅ Save to localStorage
      localStorage.setItem("userData", JSON.stringify(data));
      localStorage.setItem("userEmail", data.email);
      localStorage.setItem("loginTimestamp", Date.now().toString());
      // ⏰ Add session expiry
      const expiry = Date.now() + 24 * 60 * 60 * 1000;
      localStorage.setItem("sessionExpiry", expiry.toString());
      window.dispatchEvent(new Event("user-logged-in"));

      setToast({ message: "✅ Logged in!", type: "success" });
      navigate("/upload");
    } catch (err) {
      setToast({ message: "❌ " + err.message, type: "error" });
    } finally {
      setLoading(false);
    }
  };

  {
    toastMessage && (
      <Toast message={toastMessage} onClose={() => setToastMessage("")} />
    );
  }

  return (
    <div className="min-h-screen text-white flex items-center justify-center px-4 py-20 relative overflow-hidden">
      {/* Glow background blobs */}
      <div className="absolute inset-0 z-0">
        <div className="absolute -top-32 -left-40 w-[500px] h-[500px] bg-[#00ffc3]/15 rounded-full blur-[120px] opacity-40 animate-pulse" />
        <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-[#00ffc3]/10 rounded-full blur-[100px] opacity-40 animate-pulse" />
        <div className="absolute top-[30%] left-[35%] w-[300px] h-[300px] bg-[#00ffc3]/5 rounded-full blur-[90px] opacity-30 animate-pulse" />
      </div>

      {/* Login Card */}
      <div className="relative z-10 w-full max-w-md p-8 bg-white/5 backdrop-blur-3xl border border-white/10 rounded-2xl shadow-md">
        <h2 className="text-3xl font-bold mb-6 text-center text-[#00ffc3]">
          Welcome Back 👋
        </h2>

        {toast.message && (
          <Toast
            message={toast.message}
            type={toast.type}
            onClose={() => setToast({ message: "", type: "" })}
          />
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block mb-1 text-sm">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-[#222] rounded-lg border border-[#333] text-white focus:outline-none focus:border-[#00ffc3]"
              required
            />
          </div>

          {/* 👁️ Password */}
          <div className="relative">
            <label className="block mb-1 text-sm">Password</label>
            <input
              type={showPassword ? "text" : "password"}
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-4 py-2 pr-10 bg-[#222] rounded-lg border border-[#333] text-white focus:outline-none focus:border-[#00ffc3]"
              required
            />
            <div
              className="absolute right-3 top-[38px] cursor-pointer text-gray-400 hover:text-[#00ffc3]"
              onClick={() => setShowPassword((prev) => !prev)}
            >
              {showPassword ? (
                <AiFillEyeInvisible size={20} />
              ) : (
                <AiFillEye size={20} />
              )}
            </div>
          </div>

          <button
            type="submit"
            className="mt-8 w-full px-8 py-3 bg-[#00ffc3] text-black font-semibold rounded-xl shadow-md hover:bg-[#02e6b0] transition-all duration-300 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        <p className="mt-4 text-center text-sm">
          Don’t have an account?{" "}
          <Link to="/register" className="text-[#00ffc3] hover:underline">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
