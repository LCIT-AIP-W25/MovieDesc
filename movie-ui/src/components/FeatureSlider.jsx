import React from "react";
import { motion } from "framer-motion";

const features = [
  {
    title: "Scene Detection",
    desc: "Split your video into meaningful scenes with one click.",
    icon: "🎬",
  },
  {
    title: "Transcription",
    desc: "Accurate subtitle-like transcript for every chapter.",
    icon: "🔊",
  },
  {
    title: "Summarization",
    desc: "Quickly understand each scene with AI-generated summaries.",
    icon: "📝",
  },
  {
    title: "Downloadable Output",
    desc: "Export chapters, transcript, and summary in one file.",
    icon: "💾",
  },
];

function FeatureSlider() {
  return (
    <div className="relative py-16 px-4 z-10">
      <h2 className="text-3xl md:text-4xl text-center text-teal-400 font-bold mb-10">
        What MovieDesc Can Do
      </h2>
      <div className="flex gap-6 overflow-x-auto scrollbar-hide px-2">
        {features.map((feature, idx) => (
          <motion.div
            key={idx}
            whileHover={{ scale: 1.05 }}
            className="min-w-[280px] md:min-w-[300px] rounded-2xl p-6 bg-black/40 backdrop-blur-xl border border-teal-500 shadow-lg flex-shrink-0 transition-all duration-300"
          >
            <div className="text-5xl mb-4">{feature.icon}</div>
            <h3 className="text-xl font-semibold text-teal-300 mb-2">
              {feature.title}
            </h3>
            <p className="text-gray-300">{feature.desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export default FeatureSlider;
