<script setup lang="ts">
defineProps<{
  title: string
  text: string
  icon: 'grape' | 'shield' | 'book'
}>()
</script>

<template>
  <div class="flex flex-col items-center text-center">
    <!-- Круг с иконкой в фирменном цвете -->
    <span class="mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-[#8f3d42] text-white lg:h-[72px] lg:w-[72px]">
      <svg
        v-if="icon === 'grape'"
        class="h-8 w-8 lg:h-9 lg:w-9"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
      >
        <circle cx="9" cy="10" r="2.2" />
        <circle cx="15" cy="10" r="2.2" />
        <circle cx="12" cy="13" r="2.2" />
        <circle cx="9" cy="15" r="2.2" />
        <circle cx="15" cy="15" r="2.2" />
        <path d="M12 7V3" stroke-linecap="round" />
      </svg>

      <svg
        v-else-if="icon === 'shield'"
        class="h-8 w-8 lg:h-9 lg:w-9"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
      >
        <path d="M12 3 5 6v6c0 4 3 7 7 9 4-2 7-5 7-9V6l-7-3Z" />
        <path d="m9 12 2 2 4-4" />
      </svg>

      <svg
        v-else
        class="h-8 w-8 lg:h-9 lg:w-9"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
      >
        <path d="M4 5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5Z" />
        <path d="M9 3v18M13 8h3M13 12h3M13 16h3" />
      </svg>
    </span>

    <h3 class="mb-3 text-base font-semibold text-ink lg:text-lg">
      {{ title }}
    </h3>

    <p class="max-w-[280px] text-sm leading-relaxed text-ink-soft lg:text-[15px]">
      {{ text }}
    </p>
  </div>
</template>