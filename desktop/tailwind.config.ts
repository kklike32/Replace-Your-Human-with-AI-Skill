import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#FDFCF8",
        foreground: "#2C2C24",
        primary: "#5D7052",
        "primary-foreground": "#F3F4F1",
        secondary: "#C18C5D",
        "secondary-foreground": "#FFFFFF",
        accent: "#E6DCCD",
        "accent-foreground": "#44443A",
        muted: "#F0EBE5",
        "muted-foreground": "#6B6B5F",
        border: "#DED8CF",
        destructive: "#A85448",
      },
      boxShadow: {
        soft: "0 4px 20px -2px rgba(93, 112, 82, 0.15)",
        float: "0 10px 40px -10px rgba(193, 140, 93, 0.2)",
      },
      fontFamily: {
        serif: ["Fraunces", "ui-serif", "Georgia", "serif"],
        sans: ["Nunito", "Avenir Next", "Helvetica Neue", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
