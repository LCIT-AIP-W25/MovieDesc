import React from "react";

const features = [
  {
    title: "Auto Chaptering",
    description: "AI detects scenes and generates chapters instantly.",
  },
  {
    title: "Summarization",
    description: "Get concise summaries for long-form videos in seconds.",
  },
  {
    title: "Transcription",
    description: "Full transcript generation with speaker and time codes.",
  },
  {
    title: "Video Insights",
    description: "See key moments and structure for faster editing.",
  },
];

const Features = () => {
  return (
    <section
      id="features"
      className="relative px-6 py-32 text-white overflow-hidden z-10"
    >
      <div className="relative z-10 max-w-7xl mx-auto">
        <div className="flex items-center justify-center mb-12 space-x-2">
          <hr className="flex-grow border-t-2 border-[#00ffc3] w-1/4" />
          <h2 className="text-4xl md:text-5xl font-bold text-[#00ffc3] whitespace-nowrap">
            Features
          </h2>
          <hr className="flex-grow border-t-2 border-[#00ffc3] w-1/4" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white/5 backdrop-blur-3xl border border-white/10 rounded-2xl p-6 text-white shadow-md hover:shadow-[#00ffc3]/30 hover:scale-105 transition-all duration-300"
            >
              <h3 className="text-xl font-bold text-[#00ffc3] mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-300">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
