<script setup lang="ts">
const isOpen = ref(false)

const nav = [
  { label: 'Истории в бокале', href: 'https://vino-svoe.ru/articles' },
  { label: 'Свои вина', href: 'https://vino-svoe.ru/wines' },
  { label: 'События', href: 'https://vino-svoe.ru/events' },
  { label: 'Винные туры', href: 'https://vino-svoe.ru/tours' },
  { label: 'Винодельни и регионы', href: 'https://vino-svoe.ru/wineries' },
  { label: 'Винный Барометр', href: 'https://vino-svoe.ru/surveys/vinnyj-barometr' }
]
</script>

<template>
  <header class="fixed left-0 top-0 z-50 w-full">
    <div class="mx-auto w-full max-w-[1440px] px-4 sm:px-6 lg:px-10">
      <div class="mt-6 flex h-[64px] items-center justify-between gap-4 rounded-full bg-[#efdbc64d] px-4 backdrop-blur-[10px] transition-all duration-300 lg:h-[80px] lg:px-6">
        <NuxtLink to="/" class="shrink-0">
          <img
            src="/svg/logo/svoe-vino-logo.svg"
            alt="Своё Вино"
            class="h-9 w-auto lg:h-11"
          />
        </NuxtLink>

        <nav class="hidden flex-1 items-center justify-center gap-6 xl:flex 2xl:gap-8">
          <a
            v-for="item in nav"
            :key="item.href"
            :href="item.href"
            target="_blank"
            rel="noopener"
            class="whitespace-nowrap font-sans text-[15px] leading-none text-[#2c2a28] transition-colors duration-300 hover:text-[#9a948f] lg:text-[16px]"
          >
            {{ item.label }}
          </a>
        </nav>

        <div class="ml-auto flex shrink-0 items-center gap-2 xl:ml-0">
          <NuxtLink
            to="/scan"
            class="btn-wine-round h-11 w-11 shrink-0 lg:h-12 lg:w-12"
            aria-label="Сканер вина"
          >
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 8V5.5A1.5 1.5 0 0 1 5.5 4H8M16 4h2.5A1.5 1.5 0 0 1 20 5.5V8M20 16v2.5A1.5 1.5 0 0 1 18.5 20H16M8 20H5.5A1.5 1.5 0 0 1 4 18.5V16" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          </NuxtLink>

          <button
            class="flex h-11 w-11 items-center justify-center rounded-full text-[#2c2a28] transition hover:bg-black/5 xl:hidden"
            aria-label="Меню"
            @click="isOpen = !isOpen"
          >
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path v-if="!isOpen" d="M4 7h16M4 12h16M4 17h16" />
              <path v-else d="M6 6l12 12M18 6 6 18" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="isOpen" class="xl:hidden">
        <div class="mx-auto w-full max-w-[1440px] px-4 pb-4 sm:px-6 lg:px-10">
          <nav class="flex flex-col rounded-3xl bg-[#efdbc6] p-2 backdrop-blur-xl">
            <a
              v-for="item in nav"
              :key="item.href"
              :href="item.href"
              target="_blank"
              rel="noopener"
              class="rounded-2xl px-5 py-3.5 font-sans text-[16px] text-[#2c2a28] transition hover:bg-black/5"
              @click="isOpen = false"
            >
              {{ item.label }}
            </a>

            <NuxtLink
              to="/scan"
              class="btn-wine mt-1 w-full font-sans"
              @click="isOpen = false"
            >
              Сканер вина
            </NuxtLink>
          </nav>
        </div>
      </div>
    </Transition>
  </header>
</template>