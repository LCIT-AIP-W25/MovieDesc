import React, { useEffect } from "react";
import { useLocation } from "react-router-dom";

import Carousel from "../components/Carousel";
import Slider from "../components/Slider";
import Upload from "../components/Upload";
import About from "../components/About";
import Contact from "../components/Contact";
import UseCases from "../components/UseCases";
import Chapters from "../components/Chapters"; // Optional

const Home = () => {
  const location = useLocation();

  useEffect(() => {
    const sectionId = location.state?.scrollTo;
    if (sectionId) {
      const el = document.getElementById(sectionId.toLowerCase());
      if (el) {
        setTimeout(() => {
          el.scrollIntoView({ behavior: "smooth" });
        }, 100); // slight delay to ensure section is rendered
      }
    }
  }, [location]);

  return (
    <>
      <section id="home">
        <Carousel />
      </section>
      <section id="feature">
        <Slider />
      </section>
      <section id="usecases">
        <UseCases />
      </section>
      <section id="upload">
        <Upload />
      </section>
      <section id="about">
        <About />
      </section>
      <section id="contact">
        <Contact />
      </section>
    </>
  );
};

export default Home;
