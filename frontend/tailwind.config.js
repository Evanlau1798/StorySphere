// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // <-- 新增或修改這一行
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: { // (可選) 添加更美觀的字體
        sans: ['"Noto Sans TC"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}