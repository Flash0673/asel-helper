<script setup lang="ts">
import type { WineCard, WineProfile } from '~/types/wine'
import { wineMatches } from '~/utils/wineCatalog'
const props = defineProps<{ wines: WineCard[]; title: string; subtitle?: string; profile?: WineProfile; catalogLink?: { href: string; applied: string[]; unsupported: string[] } }>()
const totalSlides = computed(() => props.wines.length + (props.catalogLink ? 1 : 0))
const shelf = ref<HTMLElement | null>(null)
const canPrev = ref(false)
const canNext = ref(false)
const active = ref(1)
function update() {
  const el = shelf.value
  if (!el) return
  canPrev.value = el.scrollLeft > 2
  canNext.value = el.scrollLeft + el.clientWidth < el.scrollWidth - 2
  const item = el.firstElementChild as HTMLElement | null
  const gap = parseFloat(getComputedStyle(el).columnGap) || 20
  active.value = Math.min(totalSlides.value, Math.round(el.scrollLeft / ((item?.offsetWidth ?? 260) + gap)) + 1)
}
function move(direction: number) {
  const el = shelf.value
  if (!el) return
  el.scrollBy({ left: direction * el.clientWidth, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' })
}
function onKey(event: KeyboardEvent) {
  if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return
  event.preventDefault()
  if (event.key === 'Home' || event.key === 'End') shelf.value?.scrollTo({ left: event.key === 'Home' ? 0 : shelf.value.scrollWidth })
  else move(event.key === 'ArrowRight' ? 1 : -1)
}
let observer: ResizeObserver | undefined
onMounted(() => { observer = new ResizeObserver(update); if (shelf.value) observer.observe(shelf.value); update() })
onBeforeUnmount(() => observer?.disconnect())
watch(() => props.wines, async () => { await nextTick(); shelf.value?.scrollTo({ left: 0 }); update() })
</script>
<template>
  <section class="wine-carousel" role="region" aria-roledescription="карусель" :aria-label="title">
    <div class="shelf-heading">
      <div><h2>{{ title }}</h2><p v-if="subtitle">{{ subtitle }}</p></div>
      <div class="shelf-controls">
        <button type="button" class="circle-button" :disabled="!canPrev" aria-label="Предыдущие вина" @click="move(-1)"><ResultIcon name="chevron" class="rotate-180" /></button>
        <button type="button" class="circle-button" :disabled="!canNext" aria-label="Следующие вина" @click="move(1)"><ResultIcon name="chevron" /></button>
      </div>
    </div>
    <div ref="shelf" class="wine-shelf" tabindex="0" aria-label="Вина. Листайте свайпом или стрелками на клавиатуре" @scroll.passive="update" @keydown="onKey">
      <a v-for="(wine, index) in wines" :key="wine.slug" :href="wine.url" class="recommendation-card" :aria-label="`${wine.name}, ${wine.winery}, ${wine.category}. Открыть в каталоге`">
        <div class="recommendation-image">
          <WinePhoto :src="wine.image" :name="wine.name" :priority="index < 4" />
          <span v-if="wine.rating !== null" class="wine-rating"><ResultIcon name="star" />{{ wine.rating.toLocaleString('ru-RU', { maximumFractionDigits: 2 }) }}</span>
          <span class="card-open"><ResultIcon name="arrow" /></span>
        </div>
        <div class="recommendation-copy">
          <p class="card-winery">{{ wine.winery }}</p>
          <h3>{{ wine.name }}</h3>
          <p class="card-category">{{ wine.category }}</p>
          <p class="card-vintage">{{ wine.vintage ? `${wine.vintage} год` : 'Год не указан' }}<span aria-hidden="true"> · </span>{{ wine.region }}</p>
          <p v-if="wine.foodPairing.length" class="card-dishes"><span>К блюдам</span>{{ wine.foodPairing.join(' · ') }}</p>
          <span v-if="profile && wineMatches(wine, profile).includes('Тот же сорт')" class="match-tag">Тот же сорт винограда</span>
        </div>
      </a>
      <a v-if="catalogLink" :href="catalogLink.href" class="recommendation-card catalog-end-card" aria-label="Смотреть в каталоге с выбранными фильтрами">
        <span class="catalog-end-icon"><ResultIcon name="arrow" /></span>
        <h3>Больше похожих вин</h3>
        <p>{{ catalogLink.applied.length ? 'Продолжите поиск с выбранными фильтрами на сайте «Своё Вино».' : 'Откройте полный каталог российских вин.' }}</p>
        <ul v-if="catalogLink.applied.length" class="catalog-filter-tags"><li v-for="filter in catalogLink.applied" :key="filter">{{ filter }}</li></ul>
        <p v-if="catalogLink.unsupported.length" class="catalog-filter-note">Уточните в каталоге: {{ catalogLink.unsupported.join(', ') }}.</p>
        <span class="catalog-end-action">Смотреть в каталоге<ResultIcon name="arrow" /></span>
      </a>
    </div>
    <div class="shelf-foot"><span>{{ catalogLink ? 'В конце подборки — полный каталог' : 'Листайте, чтобы посмотреть ещё' }}</span><span aria-live="polite">{{ active }} / {{ totalSlides }}</span></div>
  </section>
</template>
