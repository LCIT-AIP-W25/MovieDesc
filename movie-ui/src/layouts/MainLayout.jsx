import React, { useState, useEffect } from "react";
import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Toast from "../components/Toast";

const MainLayout = () => {
  const [toastMessage, setToastMessage] = useState("");

  useEffect(() => {
    const handleLogout = () => {
      setToastMessage("Session expired. Please log in again.");
    };

    window.addEventListener("user-logged-out", handleLogout);

    return () => {
      window.removeEventListener("user-logged-out", handleLogout);
    };
  }, []);

  return (
    <div className="min-h-screen relative text-white">
      {/* 🔒 Fixed Gradient Background */}
      <div className="fixed inset-0 -z-10 bg-main-gradient bg-no-repeat bg-cover" />

      {toastMessage && (
        <Toast message={toastMessage} onClose={() => setToastMessage("")} />
      )}

      <Navbar />
      <main className="!p-0 !pt-0 !mt-0 !mb-0">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};

export default MainLayout;
