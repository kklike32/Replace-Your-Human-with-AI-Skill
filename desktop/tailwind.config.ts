import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        mist: "#e2e8f0",
        sand: "#f8fafc",
        coral: "#f97316",
        mint: "#0f766e",
        sky: "#0f766e",
      },
      boxShadow: {
        panel: "0 20px 60px rgba(15, 23, 42, 0.12)",
      },
      fontFamily: {
        sans: ["Space Grotesk", "Avenir Next", "Helvetica Neue", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
