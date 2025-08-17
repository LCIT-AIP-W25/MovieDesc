// src/components/Hero.jsx

import React from "react";
import { motion } from "framer-motion";

const Hero = () => {
  return (
    <div className="relative h-[calc(100vh-65px)] w-full bg-[#121212] py-20 px-6 text-white">
  {/* Background Image */}
  <img
    src="https://images.unsplash.com/photo-1607746882042-944635dfe10e"
    alt="Hero Background"
    className="w-full h-full object-cover"
  />

  {/* Overlay content */}
  <div className="absolute inset-0 flex flex-col items-center justify-center text-center bg-black bg-opacity-40 px-4">
    <h1 className="text-4xl md:text-6xl font-bold text-[#00ffc3]">
      Turn Videos into Smart Stories
    </h1>
    <p className="text-lg md:text-xl text-white mt-4 max-w-2xl">
      Upload a video and automatically get scene-based chapters, summaries, and transcripts – powered by AI.
    </p>
    <button className="mt-6 bg-[#00ffc3] text-black px-6 py-3 rounded-full font-semibold hover:bg-[#00e2b0] transition-all duration-300">
      Get Started
    </button>
  </div>
</div>

  );
};

export default Hero;
