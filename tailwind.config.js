/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html", // Scan HTML files in templates folder
    "./static/js/**/*.js"    // Scan JS files for dynamic classes (optional but good practice)
  ],
  darkMode: 'class',  // Enable class-based dark mode
  theme: {
    extend: {},
  },
  plugins: [],
}
