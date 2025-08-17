import React from "react";

const Contact = () => {
  return (
    <section className="relative px-6 py-16 text-white" id="contact">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-center mb-12 space-x-2">
          <hr className="flex-grow border-t-2 border-[#00ffc3] w-1/4" />
          <h2 className="text-4xl md:text-5xl font-bold text-[#00ffc3] whitespace-nowrap">
            Contact Us
          </h2>
          <hr className="flex-grow border-t-2 border-[#00ffc3] w-1/4" />
        </div>

        <form className="space-y-6 bg-white/5 backdrop-blur-3xl border border-white/10 rounded-2xl p-6 text-white shadow-md">
          <div>
            <label className="block text-sm mb-1">Name</label>
            <input
              type="text"
              placeholder="Your Name"
              className="w-full px-4 py-2 bg-[#222] text-white border border-[#333] rounded-lg focus:outline-none focus:border-[#00ffc3]"
              required
            />
          </div>

          <div>
            <label className="block text-sm mb-1">Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              className="w-full px-4 py-2 bg-[#222] text-white border border-[#333] rounded-lg focus:outline-none focus:border-[#00ffc3]"
              required
            />
          </div>

          <div>
            <label className="block text-sm mb-1">Message</label>
            <textarea
              rows="5"
              placeholder="How can we help you?"
              className="w-full px-4 py-2 bg-[#222] text-white border border-[#333] rounded-lg focus:outline-none focus:border-[#00ffc3]"
              required
            ></textarea>
          </div>

          <button
            type="submit"
            className="block w-full mt-4 px-4 py-2 bg-[#00ffc3] text-black text-md font-semibold rounded-xl shadow-md hover:bg-[#02e6b0] transition-all duration-300"
          >
            Send Message
          </button>
        </form>
      </div>
    </section>
  );
};

export default Contact;
