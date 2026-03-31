/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: '#0a0f12',
          surface: '#121a21',
          primary: '#00ff41',
          secondary: '#008f11',
          accent: '#00ccff',
          danger: '#ff003c',
          warning: '#ffb300',
          text: '#e0e0e0',
          muted: '#8091a5'
        }
      },
      fontFamily: {
        mono: ['"Fira Code"', '"Roboto Mono"', 'monospace'],
        sans: ['"Inter"', 'sans-serif'],
      },
      boxShadow: {
        'glow-primary': '0 0 15px rgba(0, 255, 65, 0.4)',
        'glow-danger': '0 0 15px rgba(255, 0, 60, 0.4)',
        'glow-accent': '0 0 15px rgba(0, 204, 255, 0.4)',
      }
    },
  },
  plugins: [],
}
