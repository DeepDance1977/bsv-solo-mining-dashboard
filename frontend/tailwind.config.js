/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bsv: {
          gold: "#f7931a",
          dark: "#0d111c",
          panel: "#12263f",
        },
      },
    },
  },
  plugins: [],
};
