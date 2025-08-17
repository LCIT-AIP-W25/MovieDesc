/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        quantum: ["Quantum", "sans-serif"],
      },
      backgroundImage: {
        "main-gradient": `radial-gradient(circle at 10% 10%, rgba(0, 255, 195, 0.18) 0%, transparent 35%),   /* Top-left */
                      radial-gradient(circle at 35% 85%, rgba(0, 255, 195, 0.08) 0%, transparent 20%), /* Freestyle */
                      radial-gradient(circle at 90% 80%, rgba(0, 255, 195, 0.12) 0%, transparent 32%), /* Bottom-right */
                      linear-gradient(to bottom, #000000, #050505)` /* Dark base */,
      },
    },
  },
  plugins: [require("tailwind-scrollbar-hide")],
};
