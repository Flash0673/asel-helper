<script setup lang="ts">
import { recommendWines } from '~/utils/wineCatalog'
import { buildCatalogLink } from '~/utils/catalogLink'
const route = useRoute()
const { data: wines, status, error, refresh } = await useWineCatalog()
const { result } = useScanResult()
const wine = computed(() => wines.value.find(item => item.slug === route.params.slug))
const demo = computed(() => route.query.demo === '1' || (result.value?.demo && result.value?.wine?.slug === wine.value?.slug))
const related = computed(() => {
  if (!wine.value) return []
  const current = wine.value
  const bySlug = new Map(wines.value.map(item => [item.slug, item]))
  const recommended = current.similarSlugs.map(slug => bySlug.get(slug)).filter((item): item is NonNullable<typeof item> => !!item && item.slug !== current.slug)
  return (recommended.length ? recommended : recommendWines(wines.value, { category: current.category, grapes: current.grapes }).filter(item => item.slug !== current.slug)).slice(0, 12)
})
const facts = computed(() => wine.value ? [
  ['Производитель', wine.value.winery],
  ['Регион', wine.value.region],
  ['Категория', wine.value.category],
  ['Год', wine.value.vintage ? String(wine.value.vintage) : 'Не указан в каталоге'],
  ['Виноград', wine.value.grapes.join(', ')],
  ['Цвет', wine.value.color],
  ['Крепость', wine.value.strength],
  ['Температура подачи', wine.value.temperature],
] : [])
useHead({ title: computed(() => wine.value ? `${wine.value.name} — Своё Вино` : 'Результат — Своё Вино') })
</script>

<template>
  <div class="result-page">
    <div class="result-container">
      <nav class="result-nav" aria-label="Навигация по результатам">
        <NuxtLink to="/scan" class="back-link"><ResultIcon name="back" />К сканеру</NuxtLink>
        <span class="result-step">Сканер <span aria-hidden="true">/</span> Результат</span>
      </nav>
      <div v-if="status === 'pending'" class="result-loading" role="status"><span class="loading-ring" />Загружаем информацию о вине…</div>
      <div v-else-if="error" class="result-empty" role="alert">
        <h1>Не удалось загрузить каталог</h1><p>Проверьте подключение и попробуйте ещё раз.</p><button class="btn-wine" @click="refresh()">Повторить</button>
      </div>
      <template v-else-if="wine">
        <p v-if="demo" class="demo-note">Пример результата · данные вина из каталога, распознавание фото пока не подключено.</p>
        <div class="detail-layout">
          <header class="detail-heading">
            <p class="result-status"><span><ResultIcon name="check" /></span>Вино есть в каталоге</p>
            <p class="detail-winery">{{ wine.winery }}</p>
            <h1>{{ wine.name }}</h1>
            <div class="detail-meta">
              <span class="category-chip">{{ wine.category }}</span>
              <span v-if="wine.rating !== null" class="detail-rating"><ResultIcon name="star" /><strong>{{ wine.rating.toLocaleString('ru-RU', { maximumFractionDigits: 2 }) }}</strong><span> / 5 в каталоге</span></span>
            </div>
          </header>
          <aside class="detail-visual">
            <div class="bottle-stage">
              <span class="stage-label">СВОЁ ВИНО <span aria-hidden="true">/</span> КОЛЛЕКЦИЯ</span>
              <WinePhoto :src="wine.image" :name="wine.name" priority />
              <div class="stage-caption"><span>{{ wine.region }}</span><span>{{ wine.vintage || 'Год не указан' }}</span></div>
            </div>
            <a :href="wine.url" class="btn-wine catalog-button">Открыть в каталоге<ResultIcon name="arrow" /></a>
            <p class="photo-source">На сайте «Своё Вино»</p>
          </aside>
          <article class="detail-copy">
            <dl class="wine-facts"><div v-for="[label, value] in facts" :key="label"><dt>{{ label }}</dt><dd>{{ value }}</dd></div></dl>
            <section v-if="wine.foodPairing.length" class="food-section"><h2>С чем сочетать</h2><ul><li v-for="dish in wine.foodPairing" :key="dish">{{ dish }}</li></ul></section>
            <section class="tasting-note"><h2>Характер вина</h2><p>{{ wine.description || 'Описание этого вина пока не добавлено в каталог.' }}</p></section>
            <NuxtLink to="/scan" class="text-action"><ResultIcon name="scan" />Сканировать другое вино</NuxtLink>
          </article>
        </div>
        <WineCarousel v-if="related.length" :wines="related" :catalog-link="buildCatalogLink({ category: wine.category })" title="В том же настроении" subtitle="Похожие вина, указанные в каталоге «Своё Вино»" />
      </template>
      <div v-else class="result-empty">
        <span class="empty-icon"><ResultIcon name="search" /></span><h1>Такой страницы нет в каталоге</h1><p>Проверьте ссылку или вернитесь к сканеру.</p><NuxtLink to="/scan" class="btn-wine">К сканеру</NuxtLink><NuxtLink to="/not-found" class="text-action">Подобрать похожее вино</NuxtLink>
      </div>
    </div>
  </div>
</template>
