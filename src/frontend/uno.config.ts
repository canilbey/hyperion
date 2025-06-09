import { defineConfig, presetUno, presetIcons } from 'unocss';

export default defineConfig({
  theme: {
    colors: {
      'blue-grey-1': '#6e7f80',
      'blue-grey-2': '#536872',
      'blue-grey-3': '#708090',
      'blue-grey-4': '#536878',
      'blue-grey-5': '#36454f',
      'primary': '#708090',
      'background': '#36454f',
      'surface': '#536872',
      'accent': '#6e7f80',
      'text': '#e0e6ed',
    },
    fontFamily: {
      'sans': 'Inter, Roboto, Arial, sans-serif',
    },
    borderRadius: {
      'md': '0.75rem',
      'lg': '1.25rem',
      'full': '9999px',
    },
  },
  presets: [presetUno(), presetIcons()],
}); 