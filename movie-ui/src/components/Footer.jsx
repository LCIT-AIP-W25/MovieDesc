// src/components/Footer.jsx
import React from "react";

const Footer = () => {
  return (
    <footer className="relative z-10 w-full mt-20 border-t border-white/10 bg-[#0a0a0a]/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col md:flex-row items-center justify-between gap-6 text-gray-300 text-sm">
        {/* Left: Brand or Copyright */}
        <div className="text-center md:text-left">
          © {new Date().getFullYear()} <span className="text-[#00ffc3] font-semibold">EchoMind</span>. All rights reserved.
        </div>

        {/* Right: Optional nav or links */}
        <div className="flex space-x-6">
          <a href="#features" className="hover:text-[#00ffc3] transition">
            Features
          </a>
          <a href="#about" className="hover:text-[#00ffc3] transition">
            About
          </a>
          <a href="#contact" className="hover:text-[#00ffc3] transition">
            Contact
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
