import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "./types/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        paper: "var(--paper)",
        ink: "var(--ink)",
        mist: "var(--mist)",
        line: "var(--line)",
        accent: "var(--accent)",
        ember: "var(--ember)"
      },
      fontFamily: {
        body: ["var(--font-body)"],
        display: ["var(--font-display)"]
      },
      boxShadow: {
        panel: "0 18px 60px rgba(35, 31, 26, 0.10)"
      }
    }
  },
  plugins: []
};

export default config;
