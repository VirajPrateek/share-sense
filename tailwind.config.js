/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./sharesense/templates/**/*.html'],
  theme: {
    extend: {
      colors: {
        brand: '#006A6A', 'brand-light': '#e0f2f1', 'brand-container': '#004f4f',
        surface: '#f6faf8', 'surface-low': '#f0f4f2', 'surface-card': '#ffffff',
        'on-surface': '#181d1c', 'on-surface-light': '#5c6767',
        danger: '#ba1a1a', 'danger-bg': 'rgba(186,26,26,0.08)',
        'success-bg': 'rgba(0,106,106,0.06)',
      },
      fontFamily: { headline: ['Manrope','sans-serif'], body: ['Inter','sans-serif'] },
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries'),
  ],
}
