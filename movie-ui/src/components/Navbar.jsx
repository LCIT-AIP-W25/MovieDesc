import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { FiMenu, FiX } from "react-icons/fi";
import { FaRegUserCircle } from "react-icons/fa";

const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const toggleMenu = () => setMenuOpen(!menuOpen);
  const closeMenu = () => setMenuOpen(false);

  const navItems = [
    { label: "Home", section: "home" },
    { label: "Feature", section: "feature" },
    { label: "Upload", section: "upload" },
    { label: "About", section: "about" },
    { label: "Contact", section: "contact" },
  ];

  useEffect(() => {
    const checkLoginStatus = () => {
      const storedUser = localStorage.getItem("userData");
      const loginTime = parseInt(localStorage.getItem("loginTimestamp"), 10);
      const now = Date.now();

      // Auto logout after 24 hours (86400000 ms)
      if (storedUser && loginTime && now - loginTime > 24 * 60 * 60 * 1000) {
        localStorage.removeItem("userData");
        localStorage.removeItem("userEmail");
        localStorage.removeItem("loginTimestamp");
        window.dispatchEvent(new Event("user-logged-out")); // optional
        window.location.href = "/login"; // force logout
      }

      setIsLoggedIn(!!storedUser);
    };

    checkLoginStatus();
    const interval = setInterval(checkLoginStatus, 60 * 1000); // check every 1 minute
    return () => clearInterval(interval);
  }, []);

  const handleNavClick = (section) => {
    closeMenu();
    if (location.pathname === "/") {
      const el = document.getElementById(section);
      if (el) el.scrollIntoView({ behavior: "smooth" });
    } else {
      navigate("/", { state: { scrollTo: section } });
    }
  };

  const handleUserIconClick = () => {
    if (isLoggedIn) navigate("/profile");
    else navigate("/login");
  };

  return (
    <nav className="fixed top-0 w-full z-50 bg-[#0a0a0a]/90 backdrop-blur-md shadow-lg transition-all duration-300">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        {/* Left: Logo */}
        <a
          href="/"
          className="text-3xl font-signature text-[#00ffc3] tracking-widest"
        >
          EchoMind
        </a>

        {/* Center: Desktop Nav */}
        <div className="hidden md:flex flex-1 justify-center space-x-10 text-sm font-medium">
          {navItems.map((item) => (
            <span
              key={item.section}
              onClick={() => handleNavClick(item.section)}
              className="group relative text-white hover:text-[#00ffc3] transition-all duration-200 cursor-pointer uppercase tracking-wide"
            >
              {item.label}
              <span className="absolute left-0 -bottom-1 h-[2px] bg-[#00ffc3] w-0 group-hover:w-full transition-all duration-300"></span>
            </span>
          ))}
        </div>

        {/* Right: User Icon + Hamburger */}
        <div className="flex items-center space-x-4 md:space-x-6">
          <button onClick={handleUserIconClick} className="button-reset">
            <FaRegUserCircle className="text-white text-2xl hover:text-[#00ffc3] transition-all duration-200" />
          </button>

          <div className="md:hidden text-white text-2xl" onClick={toggleMenu}>
            {menuOpen ? <FiX /> : <FiMenu />}
          </div>
        </div>
      </div>

      {/* Mobile Dropdown */}
      <div
        className={`md:hidden bg-[#121212] text-white overflow-hidden transition-all duration-300 ease-in-out ${
          menuOpen ? "max-h-60 py-6 px-6" : "max-h-0"
        }`}
      >
        <div className="flex flex-col items-center space-y-4 text-base font-medium text-center">
          {navItems.map((item) => (
            <span
              key={item.section}
              onClick={() => handleNavClick(item.section)}
              className="hover:text-[#00ffc3] transition-all duration-200 cursor-pointer uppercase tracking-wide"
            >
              {item.label}
            </span>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
