import React from "react";

const About = () => {
  return (
    <section
      id="about"
      className="relative py-32 px-6 text-white overflow-hidden"
    >
      {/* Removed background glow blobs */}

      {/* About Content */}
      <div className="relative z-10 max-w-7xl mx-auto">
        <div className="flex items-center justify-center mb-12 space-x-2">
          <hr className="flex-grow border-t-2 border-[#00ffc3] w-1/4" />
          <h2 className="text-4xl md:text-5xl font-bold text-[#00ffc3] whitespace-nowrap">
            About Us
          </h2>
          <hr className="flex-grow border-t-2 border-[#00ffc3] w-1/4" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-20 items-center px-4">
          {/* Left: Description */}
          <div className="text-lg md:text-xl text-gray-300 leading-relaxed">
            <p className="mb-6">
              <strong className="text-[#00ffc3]">EchoMind</strong> transforms
              your long-form videos into bite-sized stories using AI.
            </p>
            <p className="mb-4">
              Whether you're a content creator, educator, or analyst — we help
              you unlock the full value of your videos through intelligent
              segmentation, summarization, and transcription.
            </p>
            <p className="text-gray-400">
              Make your videos searchable, skimmable, and ready to share. 🎬✨
            </p>
          </div>

          {/* Right: Bullet Points */}
          <ul className="text-left text-gray-300 list-disc list-inside space-y-4 text-md md:text-lg">
            <li>
              <span className="text-[#00ffc3] font-medium">
                Auto-generate chapters
              </span>{" "}
              based on scene changes
            </li>
            <li>
              <span className="text-[#00ffc3] font-medium">
                Create clean transcripts
              </span>{" "}
              with time codes
            </li>
            <li>
              <span className="text-[#00ffc3] font-medium">
                Summarize long videos
              </span>{" "}
              with a single click
            </li>
            <li>
              <span className="text-[#00ffc3] font-medium">
                Get structured video outlines
              </span>{" "}
              in seconds
            </li>
            <li>
              <span className="text-[#00ffc3] font-medium">
                Optimize for storytelling & editing
              </span>
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
};

export default About;
