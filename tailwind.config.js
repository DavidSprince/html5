/** @type {import('tailwindcss').Config} */
export default {
  content: ['./**/*.html', './assets/js/**/*.js'],
  safelist: [
    // Color utility classes referenced dynamically via data attributes / JS,
    // so the JIT scanner needs them listed explicitly.
    { pattern: /^(bg|text|border)-(orange|red|emerald|pink|blue|cyan|purple|amber|slate|violet|indigo|sky|teal|lime|fuchsia|rose)-(50|100|200|600|700)$/ },
    { pattern: /^from-(orange|red|emerald|pink|blue|cyan|purple|amber|slate|violet|indigo|sky|teal|lime|fuchsia|rose)-(500|600)$/ },
    { pattern: /^to-(orange|red|emerald|pink|blue|cyan|purple|amber|slate|violet|indigo|sky|teal|lime|fuchsia|rose|amber|green|blue|rose)-(500|800)$/ },
    { pattern: /^bg-(orange|red|emerald|pink|blue|cyan|purple|amber|slate|violet|indigo|sky|teal|lime|fuchsia|rose)-(700|800)$/, variants: ['hover'] },
    { pattern: /^ring-(orange|red|emerald|pink|blue|cyan|purple|amber|slate|violet|indigo|sky|teal|lime|fuchsia|rose)-500\/20$/ },
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
