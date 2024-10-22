/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js', // Include paths where you use Tailwind classes
  ],
  theme: {
    extend: {
      colors: {
        customBlue: '#1DA1F2',
      },
    },
  },
  plugins: [],
};
