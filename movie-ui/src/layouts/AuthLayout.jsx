// src/layouts/AuthLayout.jsx
import React from "react";
import Navbar from "../components/Navbar";

const AuthLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-[#000000] text-white">
      <Navbar />
      <main className="pt-20">{children}</main> {/* Push below fixed navbar */}
    </div>
  );
};

export default AuthLayout;
