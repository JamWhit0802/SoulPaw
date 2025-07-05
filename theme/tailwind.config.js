module.exports = {
  content: [
    // your content paths here
  ],
  theme: {
    extend: {
      colors: {
        'sp-purple': '#c39cdb',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
};
