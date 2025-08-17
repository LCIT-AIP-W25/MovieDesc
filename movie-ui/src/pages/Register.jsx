import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AiFillEye, AiFillEyeInvisible } from "react-icons/ai";

const Register = () => {
  const [formData, setFormData] = useState({
    fullname: "",
    email: "",
    password: "",
    confirmPassword: "",
    usertype: "student",
    termsAccepted: false,
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ message: "", type: "" });
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.termsAccepted) return alert("✅ Please accept terms.");
    if (formData.password !== formData.confirmPassword)
      return setToast({
        message: "❌ Password dont match" + err.message,
        type: "error",
      });

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fullname: formData.fullname,
          email: formData.email,
          password: formData.password,
          usertype: formData.usertype,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Registration failed");

      setToast({ message: "✅ Registred Successfuly!", type: "success" });
      navigate("/login");
    } catch (err) {
      if (err instanceof Error) {
        setToast({ message: "❌ " + err.message, type: "error" });
      } else {
        setToast({ message: "❌ Unexpected Error Occurred", type: "error" });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen text-white flex items-center justify-center px-4 py-20 relative overflow-hidden">
      {/* Glow background blobs */}
      {/* <div className="absolute inset-0 z-0">
        <div className="absolute -top-32 -left-40 w-[500px] h-[500px] bg-[#00ffc3]/15 rounded-full blur-[120px] opacity-40 animate-pulse" />
        <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-[#00ffc3]/10 rounded-full blur-[100px] opacity-40 animate-pulse" />
        <div className="absolute top-[30%] left-[35%] w-[300px] h-[300px] bg-[#00ffc3]/5 rounded-full blur-[90px] opacity-30 animate-pulse" />
      </div> */}

      {/* Form card */}
      <div className="relative z-10 w-full max-w-md p-8 bg-white/5 backdrop-blur-3xl border border-white/10 rounded-2xl shadow-md hover:shadow-[#00ffc3]/20 transition-all duration-300">
        <h2 className="text-3xl font-bold mb-6 text-center text-[#00ffc3]">
          Create an Account
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
            <label className="block mb-1 text-sm">Full Name</label>
            <input
              type="text"
              name="fullname"
              value={formData.fullname}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-[#222] rounded-lg border border-[#333] text-white focus:outline-none focus:border-[#00ffc3]"
              required
            />
          </div>
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

          {/* 👁️ Confirm Password */}
          <div className="relative">
            <label className="block mb-1 text-sm">Confirm Password</label>
            <input
              type={showConfirm ? "text" : "password"}
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="w-full px-4 py-2 pr-10 bg-[#222] rounded-lg border border-[#333] text-white focus:outline-none focus:border-[#00ffc3]"
              required
            />
            <div
              className="absolute right-3 top-[38px] cursor-pointer text-gray-400 hover:text-[#00ffc3]"
              onClick={() => setShowConfirm((prev) => !prev)}
            >
              {showConfirm ? (
                <AiFillEyeInvisible size={20} />
              ) : (
                <AiFillEye size={20} />
              )}
            </div>
          </div>

          <div>
            <label className="block mb-1 text-sm">User Type</label>
            <select
              name="usertype"
              value={formData.usertype}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-[#222] text-white border border-[#333] rounded-lg focus:outline-none focus:border-[#00ffc3]"
            >
              <option value="student">Student</option>
              <option value="researcher">Researcher</option>
              <option value="content_creator">Content Creator</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              name="termsAccepted"
              checked={formData.termsAccepted}
              onChange={handleChange}
              required
            />
            <label className="text-sm">
              I agree to the{" "}
              <span className="text-[#00ffc3] underline">
                Terms & Conditions
              </span>
            </label>
          </div>

          <button
            type="submit"
            className="mt-8 w-full px-8 py-3 bg-[#00ffc3] text-black font-semibold rounded-xl shadow-md hover:bg-[#02e6b0] transition-all duration-300 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? "Registering..." : "Register"}
          </button>
        </form>
        <p className="mt-4 text-center text-sm">
          Already have an account?{" "}
          <Link to="/login" className="text-[#00ffc3] hover:underline">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
