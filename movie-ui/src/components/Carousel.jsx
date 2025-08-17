import React from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination, Autoplay, EffectFade } from "swiper/modules";

import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import "swiper/css/autoplay";
import Slide1 from "../assets/carousel/Slide1.jpg";
import Slide2 from "../assets/carousel/Slide2.jpg";
import Slide3 from "../assets/carousel/Slide3.jpg";

const slides = [
  {
    id: 1,
    image: Slide1,
    heading: "Turn Videos into Smart Stories",
    subtext:
      "Upload a video and automatically get scene-based chapters, summaries, and transcripts – powered by AI.",
  },
  {
    id: 2,
    image: Slide2,
    heading: "AI-Powered Scene Detection",
    subtext:
      "Identify key moments and generate structured video breakdowns automatically.",
  },
  {
    id: 3,
    image: Slide3,
    heading: "Summarize Long Videos Instantly",
    subtext:
      "Save time and increase accessibility with concise AI-generated summaries.",
  },
];

const Carousel = () => {
  return (
    <div className="relative h-[calc(100vh-65px)] w-full mt-[65px]">
      <Swiper
        spaceBetween={0}
        slidesPerView={1}
        navigation
        pagination={{ clickable: true }}
        autoplay={{ delay: 5000 }}
        loop={true}
        modules={[Navigation, Pagination, Autoplay]}
        className="h-full w-full"
      >
        {slides.map((slide) => (
          <SwiperSlide key={slide.id}>
            <div className="relative w-full h-full">
              <img
                src={slide.image}
                alt={slide.heading}
                className="w-full h-full object-cover"
              />
              <div
                className="absolute inset-0 flex flex-col items-center justify-center text-center 
                bg-gradient-to-t from-black/60 to-black/20 backdrop-blur-md px-4"
              >
                <h1 className="text-4xl md:text-6xl text-[#00ffc3] drop-shadow-lg">
                  {slide.heading}
                </h1>
                <p className="text-lg md:text-md text-white mt-4 max-w-2xl drop-shadow">
                  {slide.subtext}
                </p>
                <button
                  className="mt-6 px-6 py-4 bg-[#00ffc3] text-black font-semibold rounded-5xl shadow-md hover:bg-[#02e6b0] transition-all duration-300 disabled:opacity-50mt-6 text-black px-6 py-3 rounded-full font-semibold 
                  hover:bg-[#00e2b0] transition-all duration-300 shadow-lg"
                  onClick={() => {
                    document
                      .getElementById("upload")
                      .scrollIntoView({ behavior: "smooth" });
                  }}
                >
                  Get Started
                </button>
              </div>
            </div>
          </SwiperSlide>
        ))}
      </Swiper>

      {/* Custom Styles for Arrows & Dots */}
      <style>
        {`
          .swiper-button-prev, .swiper-button-next {
            color: #fff;
            opacity: 0.5;
            transition: opacity 0.3s ease;
          }
          .swiper-button-prev:hover, .swiper-button-next:hover {
            opacity: 1;
          }
          .swiper-pagination-bullet {
            background: white;
            opacity: 0.5;
          }
          .swiper-pagination-bullet-active {
            background: #00ffc3;
            opacity: 1;
          }
        `}
      </style>
    </div>
  );
};

export default Carousel;
