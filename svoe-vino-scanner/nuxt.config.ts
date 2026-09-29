export default defineNuxtConfig({
  ssr: false,
  modules: ['@nuxtjs/tailwindcss'],
  css: ['~/assets/css/main.css', '~/assets/css/results.css'],
  devtools: { enabled: false },
  runtimeConfig: {
    public: {
      useMock: process.env.NUXT_PUBLIC_USE_MOCK ?? 'true',
      apiBase: process.env.NUXT_PUBLIC_API_BASE ?? ''
    }
  },
  app: {
    head: {
      htmlAttrs: { lang: 'ru' },
      title: 'Своё Вино — Сканер российского вина',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
        { name: 'theme-color', content: '#FAF7F2' },
        { name: 'description', content: 'Сканер российских вин с описанием на платформе «Своё вино»' }
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/svg/logo/svoe-vino-logo.svg' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Prata&display=swap'
        }
      ]
    }
  }
})
