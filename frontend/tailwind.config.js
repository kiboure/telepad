/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        base: {
          900: '#0b0b0c',
          800: '#121214',
          700: '#18181b',
          600: '#202024',
          500: '#27272a',
          400: '#303036',
          300: '#3a3a42',
          200: '#4a4a55',
          100: '#6b6b76'
        },
        accent: {
          500: '#b7b7be',
          400: '#c5c5cb',
          300: '#d3d3d8'
        },
        success: '#3fb67f',
        danger: '#ef5b74',
        warning: '#e7a34b'
      },
      boxShadow: {
        innerdeep: 'inset 0 0 30px rgba(0,0,0,0.6)',
      },
      borderRadius: {
        xl: '18px'
      }
    },
  },
  plugins: [],
}


