import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './app.vue'
  ],
  theme: {
    extend: {
      colors: {
        // Числовая шкала — для фонов, карточек, границ
        cream: {
          50: '#FDFBF7',
          100: '#FAF7F2',   // основной фон страницы
          200: '#F5F0EA',   // чуть темнее — для hover
          300: '#EDE5DA',
          DEFAULT: '#F5E8D3', // песочная плашка header
          light: '#FBF6EE'
        },
        // Бордо — основной акцент
        wine: {
          DEFAULT: '#A61E2A',
          dark: '#8B1A24',
          light: '#C24A55'
        },
        // Текстовые цвета
        ink: {
          DEFAULT: '#2B2B2B',
          soft: '#6B6B6B',
          muted: '#9A9A9A'
        },
        leaf: '#4A6B4A'
      },
      fontFamily: {
        serif: ['Prata', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif']
      },
      boxShadow: {
        card: '0 8px 30px rgba(43, 43, 43, 0.06)',
        soft: '0 4px 20px rgba(43, 43, 43, 0.05)'
      }
    }
  }
}