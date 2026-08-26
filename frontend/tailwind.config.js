/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'sj-primary': '#003865',
        'sj-secondary': '#d32f2f',
        'sj-accent': '#f8fafc',
      }
    },
  },
  plugins: [],
}
