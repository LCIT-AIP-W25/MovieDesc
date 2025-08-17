import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Profile = () => {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const userData = localStorage.getItem("userData");
    if (!userData) {
      navigate("/login");
    } else {
      try {
        setUser(JSON.parse(userData));
      } catch (e) {
        console.error("Error parsing user data:", e);
        localStorage.removeItem("userData");
        navigate("/login");
      }
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("userData");
    window.dispatchEvent(new Event("user-logged-in"));
    navigate("/login");
  };

  if (!user) return null;

  return (
    <div className="min-h-screen text-white flex items-center justify-center px-4 py-20 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute inset-0 z-0">
        <div className="absolute -top-32 -left-40 w-[500px] h-[500px] bg-[#00ffc3]/15 rounded-full blur-[120px] opacity-40 animate-pulse" />
        <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-[#00ffc3]/10 rounded-full blur-[100px] opacity-40 animate-pulse" />
      </div>

      {/* Profile Card */}
      <div className="relative z-10 w-full max-w-md p-8 bg-white/5 backdrop-blur-3xl border border-white/10 rounded-2xl shadow-md">
        <h2 className="text-3xl font-bold text-[#00ffc3] mb-6 text-center flex items-center justify-center gap-2">
          <span role="img" aria-label="user">
            👤
          </span>{" "}
          User Info
        </h2>

        <div className="space-y-4 text-sm">
          <p>
            <span className="font-semibold text-[#00ffc3]">Full Name:</span>{" "}
            {user.fullname || "—"}
          </p>
          <p>
            <span className="font-semibold text-[#00ffc3]">Email:</span>{" "}
            {user.email || "—"}
          </p>
          <p>
            <span className="font-semibold text-[#00ffc3]">User Type:</span>{" "}
            {user.usertype || "—"}
          </p>
        </div>

        <button
          onClick={handleLogout}
          className="mt-8 w-full px-8 py-3 bg-[#00ffc3] text-black font-semibold rounded-xl shadow-md hover:bg-[#02e6b0] transition-all duration-300 disabled:opacity-50"
        >
          Logout
        </button>
      </div>
    </div>
  );
};

export default Profile;
