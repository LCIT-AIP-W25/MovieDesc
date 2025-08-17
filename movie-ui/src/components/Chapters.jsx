import React from "react";

const chapters = [
  {
    title: "Chapter 1: Introduction",
    description: "Explore the beginning of the story and its tone.",
  },
  {
    title: "Chapter 2: Twist Revealed",
    description: "Things take a turn as key characters emerge.",
  },
  {
    title: "Chapter 3: Climax",
    description: "The tension builds with powerful revelations.",
  },
  {
    title: "Chapter 4: Resolution",
    description: "The story wraps up with a satisfying end.",
  },
];

const Chapters = () => {
  return (
    <section id="chapters" className="py-16 px-4 bg-[#111]">
      <h2 className="text-center text-3xl md:text-4xl font-bold text-white mb-12">
        Featured Chapters
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
        {chapters.map((chapter, index) => (
          <div
            key={index}
            className="bg-[#1f1f1f] border border-[#00ffc3] rounded-2xl p-6 text-white transition-transform duration-300 transform hover:scale-105 hover:shadow-[0_0_10px_#00ffc3]"
          >
            <h3 className="text-xl font-bold text-[#00ffc3] mb-2">
              {chapter.title}
            </h3>
            <p className="text-gray-300">{chapter.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Chapters;
