// src/components/BackgroundBubbles.jsx
import React from "react";

const BackgroundBubbles = () => {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
      <div className="absolute top-[-100px] left-[-100px] w-[400px] h-[400px] bg-[#00ffc3]/30 rounded-full blur-[140px]" />
      <div className="absolute top-[30%] left-[20%] w-[300px] h-[300px] bg-[#00ffc3]/20 rounded-full blur-[100px]" />
      <div className="absolute bottom-[-120px] right-[-80px] w-[500px] h-[500px] bg-[#00ffc3]/10 rounded-full blur-[180px]" />
    </div>
  );
};

export default BackgroundBubbles;
