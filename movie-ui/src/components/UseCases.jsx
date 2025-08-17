import React from "react";
import { FaVideo, FaBook, FaBrain, FaTools } from "react-icons/fa";

const useCases = [
  {
    icon: <FaVideo size={28} />,
    title: "Content Creators",
    desc: "Automatically generate chapters and summaries for YouTube, Reels, or long-form content.",
  },
  {
    icon: <FaBook size={28} />,
    title: "Educators",
    desc: "Summarize recorded lectures and presentations into digestible learning modules.",
  },
  {
    icon: <FaBrain size={28} />,
    title: "Researchers",
    desc: "Quickly extract insights from interviews, webinars, or documentary videos.",
  },
  {
    icon: <FaTools size={28} />,
    title: "Video Editors",
    desc: "Speed up editing by skipping to key scenes and auto-structuring your narrative.",
  },
];

const UseCases = () => {
  return (
    <section
      id="usecases"
      className="relative px-6 py-32 text-white overflow-hidden z-10"
    >
      <div className="relative z-10 max-w-7xl mx-auto text-center">
        <div className="flex items-center justify-center mb-12 space-x-2">
          <hr className="flex-grow border-t-2 border-[#00ffc3] w-1/4" />
          <h2 className="text-4xl md:text-5xl font-bold text-[#00ffc3] whitespace-nowrap">
            Who is EchoMind for?
          </h2>
          <hr className="flex-grow border-t-2 border-[#00ffc3] w-1/4" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 px-4">
          {useCases.map((item, i) => (
            <div
              key={i}
              className="bg-white/5 backdrop-blur-3xl p-6 rounded-2xl border border-white/10 shadow-md"
            >
              <div className="text-[#00ffc3] flex justify-center mb-4">
                {item.icon}
              </div>
              <h3 className="text-xl font-semibold mb-2 text-[#00ffc3]">
                {item.title}
              </h3>
              <p className="text-gray-300 text-sm">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default UseCases;
