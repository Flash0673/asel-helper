<template>
  <!-- HERO с фоновой картинкой -->
  <section class="relative">
    <!-- Фон -->
    <div class="absolute inset-0">
      <img
        src="/hero-vineyard.jpg"
        alt=""
        class="h-full w-full object-cover"
      />
      <div class="absolute inset-0 bg-black/15" />
    </div>

    <!-- Контент: верхний отступ = высота шапки + запас -->
    <div class="relative mx-auto w-full max-w-[1440px] px-4 pb-16 pt-[120px] sm:px-6 sm:pb-24 sm:pt-[152px] lg:px-10 lg:pb-32 lg:pt-[200px]">
      <div class="container-smooth px-5 py-8 text-center sm:px-10 sm:py-12 lg:px-16 lg:py-16">

        <p class="text-[11px] font-medium uppercase tracking-[0.22em] text-ink-soft">
          Новый сервис
        </p>

        <h1 class="font-serif text-[30px] leading-[1.08] text-ink sm:text-[44px] lg:text-[64px]">
          Сканер российского<br class="hidden sm:block" />
          вина
        </h1>

        <p class="mx-auto max-w-[560px] text-[14px] leading-relaxed text-ink-soft sm:text-[17px] lg:text-lg">
          Наведите камеру на этикетку — и найдите вино в каталоге «Своё Вино» с подробным описанием.
        </p>

        <div class="mt-2 flex justify-center sm:mt-4">
          <NuxtLink to="/scan" class="btn-wine">
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M4 8V5.5A1.5 1.5 0 0 1 5.5 4H8M16 4h2.5A1.5 1.5 0 0 1 20 5.5V8M20 16v2.5A1.5 1.5 0 0 1 18.5 20H16M8 20H5.5A1.5 1.5 0 0 1 4 18.5V16" />
              <circle cx="12" cy="12" r="3" />
            </svg>
            Сканировать вино
          </NuxtLink>
        </div>
      </div>
    </div>
  </section>

  <!-- 3 ПРЕИМУЩЕСТВА -->
  <section class="relative z-10 mt-12 lg:mt-16">
    <div class="mx-auto w-full max-w-[1240px] px-6 lg:px-10">
      <div class="grid gap-10 rounded-[32px] bg-white px-8 py-12 shadow-card sm:grid-cols-3 sm:gap-8 lg:px-16 lg:py-16">
        <AdvantageCard
          icon="grape"
          title="Только российские вина"
          text="Уникальный каталог отечественных производителей и виноделен"
        />
        <AdvantageCard
          icon="shield"
          title="Проверенное качество"
          text="Рейтинг Роскачества и экспертные оценки"
        />
        <AdvantageCard
          icon="book"
          title="Подробные описания"
          text="Сорт, регион, вкус, рекомендации по подаче"
        />
      </div>
    </div>
  </section>

  <!-- ОТКРОЙ КУЛЬТУРУ -->
  <section class="mt-16 lg:mt-24">
    <div class="mx-auto w-full max-w-[1240px] px-6 lg:px-10">
      <div class="grid items-center gap-8 lg:grid-cols-2 lg:gap-16">
        <div>
          <h2 class="font-serif text-[28px] leading-tight text-ink sm:text-[36px] lg:text-[44px]">
            Открой культуру<br /> российского вина
          </h2>
          <p class="mt-5 max-w-[480px] text-[15px] leading-relaxed text-ink-soft sm:text-base">
            Более 60% рынка — это вина, сделанные в России. Сканер помогает узнать каждое из них: производителя, регион, сорт и историю.
          </p>
          <NuxtLink to="/scan" class="btn-wine mt-8">
            Попробовать сканер
          </NuxtLink>
        </div>
        <div class="aspect-[5/4] overflow-hidden rounded-[32px] bg-cream-200">
          <img
            src="/vine1.jpg"
            alt="Виноградники России"
            class="h-full w-full object-cover"
          />
        </div>
      </div>
    </div>
  </section>
</template>