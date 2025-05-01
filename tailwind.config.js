/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html", // Scan HTML files in templates folder
    "./static/js/**/*.js"    // Scan JS files for dynamic classes (optional but good practice)
  ],
  darkMode: 'class',  // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        whisky: {
          primary: '#553d25',
          dark: '#272522',
          accent: '#77542d',
          light: '#a38b69',
          darker: '#2b1f13',
        },
      },
    },
  },
  plugins: [],
}
