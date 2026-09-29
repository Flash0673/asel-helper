<script setup lang="ts">
import { DEMO_WINE_SLUG } from '~/utils/wineCatalog'
type ScanState = 'idle' | 'preview' | 'uploading' | 'error'

const state = ref<ScanState>('idle')
const error = ref<string | null>(null)
const previewUrl = ref<string | null>(null)
const file = ref<File | null>(null)
const progress = ref(0)
const { scanWine, useMock } = useWineApi()
const { setResult, photo } = useScanResult()
const scenario = ref<'found' | 'not-found'>('found')
const { data: catalog, error: catalogError } = await useWineCatalog()

const cameraInput = ref<HTMLInputElement | null>(null)
const galleryInput = ref<HTMLInputElement | null>(null)

const MAX_SIZE = 15 * 1024 * 1024

function onFile(e: Event) {
  const input = e.target as HTMLInputElement
  const f = input.files?.[0]
  if (!f) return

  if (!f.type.startsWith('image/')) {
    error.value = 'Это не изображение. Загрузите фото этикетки (JPG, PNG, HEIC).'
    state.value = 'error'
    input.value = ''
    return
  }
  if (f.size > MAX_SIZE) {
    error.value = 'Файл слишком большой. Максимум 15 МБ.'
    state.value = 'error'
    input.value = ''
    return
  }

  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  file.value = f
  previewUrl.value = URL.createObjectURL(f)
  error.value = null
  progress.value = 0
  state.value = 'preview'
}

function reset() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = null
  file.value = null
  error.value = null
  progress.value = 0
  state.value = 'idle'
  if (cameraInput.value) cameraInput.value.value = ''
  if (galleryInput.value) galleryInput.value.value = ''
}

async function submit() {
  if (!file.value) return
  state.value = 'uploading'
  progress.value = 0

  try {
    if (catalogError.value) throw new Error('Не удалось загрузить каталог. Обновите страницу и попробуйте ещё раз.')
    const form = new FormData()
    form.append('image', file.value)

    const res = await scanWine(form, (p) => (progress.value = p), scenario.value)
    setResult(res, previewUrl.value)

    if (!res.found || !res.wine || !catalog.value.some(wine => wine.slug === res.wine?.slug)) {
      await navigateTo({ path: '/not-found', query: { from: 'scan', ...(res.demo ? { demo: '1' } : {}) } })
      return
    }
    await navigateTo({ path: `/wine/${encodeURIComponent(res.wine.slug)}`, query: res.demo ? { demo: '1' } : {} })
  } catch (e: any) {
    error.value = e?.message ?? 'Не удалось отправить фото. Попробуйте ещё раз.'
    state.value = 'error'
  }
}

onBeforeUnmount(() => {
  if (previewUrl.value && previewUrl.value !== photo.value) URL.revokeObjectURL(previewUrl.value)
})
</script>

<template>
  <section class="relative flex flex-1 flex-col">
    <!-- Фон, растянутый до футера (-bottom-16 компенсирует mt-16 у футера) -->
    <div class="absolute inset-x-0 top-0 -bottom-16">
      <img
        src="/vine2.jpg"
        alt=""
        class="h-full w-full object-cover"
      />
      <div class="absolute inset-0 bg-black/15" />
    </div>

    <!-- Контент -->
    <div class="relative mx-auto flex w-full max-w-[1440px] flex-1 flex-col justify-center px-4 pb-16 pt-[120px] sm:px-6 sm:pb-24 sm:pt-[152px] lg:px-10 lg:pb-32 lg:pt-[200px]">
      <div class="container-smooth scan-panel mx-auto max-w-2xl px-5 py-8 text-center sm:px-10 sm:py-12 lg:px-14 lg:py-14">

        <p class="text-[11px] font-medium uppercase tracking-[0.22em] text-ink-soft">
          Сканер
        </p>

        <h1 class="font-serif text-[30px] leading-[1.08] text-ink sm:text-[44px] lg:text-[56px]">
          Сканировать вино
        </h1>

        <p class="mx-auto max-w-[480px] text-[14px] leading-relaxed text-ink-soft sm:text-[16px]">
          Сфотографируйте этикетку или загрузите из галереи — и мы найдём вино в каталоге «Своё Вино».
        </p>

      <aside v-if="useMock" class="scan-demo">
        <p>Демонстрация интерфейса. Распознавание по фото пока не подключено. Можно посмотреть оба результата на данных каталога.</p>
        <div class="scan-demo-links">
          <NuxtLink :to="`/wine/${DEMO_WINE_SLUG}?demo=1`">Вино есть в каталоге</NuxtLink>
          <NuxtLink to="/not-found?demo=1">Вина нет в каталоге</NuxtLink>
        </div>
      </aside>

        <!-- Скрытые input'ы -->
        <input
          ref="cameraInput"
          type="file"
          accept="image/*"
          capture="environment"
          class="hidden"
          @change="onFile"
        />
        <input
          ref="galleryInput"
          type="file"
          accept="image/*"
          class="hidden"
          @change="onFile"
        />

        <!-- IDLE -->
        <div v-if="state === 'idle'" class="grid gap-3 sm:grid-cols-2">
          <button class="btn-wine w-full" @click="cameraInput?.click()">
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M4 8h3l1.5-2h7L17 8h3v11H4V8Z" />
              <circle cx="12" cy="13" r="3.5" />
            </svg>
            Сделать фото
          </button>

          <button class="btn-wine-outline w-full" @click="galleryInput?.click()">
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <rect x="3" y="5" width="18" height="14" rx="2" />
              <circle cx="8.5" cy="10.5" r="1.5" />
              <path d="m4 17 5-5 4 4 3-2 4 4" />
            </svg>
            Выбрать из галереи
          </button>
        </div>

        <!-- PREVIEW -->
        <div v-else-if="state === 'preview' && previewUrl" class="flex flex-col items-center">
          <div class="relative w-full overflow-hidden rounded-2xl bg-black/20">
            <img
              :src="previewUrl"
              alt="Превью этикетки"
              class="mx-auto max-h-[360px] w-auto object-contain"
              @error="error = 'Не удалось открыть изображение. Попробуйте JPG, PNG или WebP.'; state = 'error'"
            />
          </div>
          <p class="mt-3 max-w-full truncate text-xs text-ink-soft">{{ file?.name }}</p>
          <fieldset v-if="useMock" class="demo-scenario">
            <legend>Какой пример показать</legend>
            <label><input v-model="scenario" type="radio" value="found" />Есть в каталоге</label>
            <label><input v-model="scenario" type="radio" value="not-found" />Нет в каталоге</label>
          </fieldset>

          <div class="mt-5 grid w-full gap-3 sm:grid-cols-2">
            <button class="btn-wine-outline w-full" @click="reset">
              Выбрать другое
            </button>
            <button class="btn-wine w-full" @click="submit">
              {{ useMock ? 'Показать результат' : 'Найти вино' }}
            </button>
          </div>
        </div>

        <!-- UPLOADING -->
        <div v-else-if="state === 'uploading'" class="flex flex-col items-center py-2">
          <div v-if="previewUrl" class="relative w-full overflow-hidden rounded-2xl">
            <img
              :src="previewUrl"
              alt=""
              class="mx-auto max-h-[300px] w-auto object-contain opacity-60"
            />
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="h-10 w-10 animate-spin rounded-full border-2 border-[#8f3d42]/20 border-t-[#8f3d42]" />
            </div>
          </div>
          <p class="mt-5 text-sm text-ink">Ищем вино в каталоге…</p>
          <div class="mt-3 h-1 w-full max-w-xs overflow-hidden rounded-full bg-white/40">
            <div class="h-full bg-[#8f3d42] transition-all" :style="{ width: `${progress}%` }" />
          </div>
        </div>

        <!-- ERROR -->
        <div v-else-if="state === 'error'" class="flex flex-col items-center py-2 text-center">
          <span class="flex h-12 w-12 items-center justify-center rounded-full bg-[#8f3d42] text-white">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M12 8v5M12 16h.01" />
              <circle cx="12" cy="12" r="9" />
            </svg>
          </span>
          <p class="mt-4 max-w-sm text-sm text-ink">{{ error }}</p>
          <button class="btn-wine mt-5" @click="reset">
            Попробовать снова
          </button>
        </div>

        <p class="mt-6 text-xs leading-relaxed text-ink-soft">
          Хороший результат получается при хорошем освещении и чётком изображении этикетки.
        </p>
      </div>
    </div>
  </section>
</template>
