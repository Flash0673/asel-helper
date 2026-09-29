<script setup lang="ts">
import type { WineProfile } from '~/types/wine'
import { DEMO_PROFILE, availableWineFilters, reconcileWineProfile, recommendWines } from '~/utils/wineCatalog'
import { buildCatalogLink } from '~/utils/catalogLink'
const route = useRoute()
const { result, photo } = useScanResult()
const { data: wines, status, error, refresh } = await useWineCatalog()
const demo = computed(() => route.query.demo === '1' || !!result.value?.demo)
const initial: WineProfile = route.query.demo === '1' ? DEMO_PROFILE : result.value?.profile ?? {}
const category = ref(initial.category ?? '')
const grape = ref(initial.grapes?.[0] ?? '')
const region = ref(initial.region ?? '')
const dish = ref(initial.dish ?? '')
const vintage = ref(initial.vintage ?? null)
const adjustedParameters = ref(false)
const profile = computed<WineProfile>(() => ({ category: category.value, grapes: grape.value ? [grape.value] : [], region: region.value, vintage: vintage.value, dish: dish.value }))
const hasParameters = computed(() => Boolean(category.value || grape.value || region.value || vintage.value || dish.value))
const filters = computed(() => availableWineFilters(wines.value, profile.value))
watch(wines, catalog => {
  if (!catalog.length) return
  const compatible = reconcileWineProfile(catalog, profile.value)
  category.value = compatible.profile.category ?? ''
  grape.value = compatible.profile.grapes?.[0] ?? ''
  region.value = compatible.profile.region ?? ''
  dish.value = compatible.profile.dish ?? ''
  adjustedParameters.value = compatible.removed.length > 0
}, { immediate: true })
const recommendations = computed(() => recommendWines(wines.value, profile.value))
const catalogLink = computed(() => buildCatalogLink(profile.value))
const subtitle = computed(() => dish.value ? `К блюду «${dish.value}» и по другим выбранным характеристикам. Подробнее — в карточке вина.` : 'Подборка по выбранным характеристикам. Выберите вино, чтобы открыть его в каталоге.')
const showPhoto = computed(() => route.query.from === 'scan' && !!photo.value)
function clear() { category.value = ''; grape.value = ''; region.value = ''; dish.value = ''; vintage.value = null; adjustedParameters.value = false }
useHead({ title: 'Похожие вина — Своё Вино' })
</script>

<template>
  <div class="result-page">
    <div class="result-container">
      <nav class="result-nav" aria-label="Навигация по результатам"><NuxtLink to="/scan" class="back-link"><ResultIcon name="back" />К сканеру</NuxtLink><span class="result-step">Сканер <span aria-hidden="true">/</span> Результат</span></nav>
      <p v-if="demo" class="demo-note">Пример результата · параметры для подбора заданы для демонстрации.</p>
      <section class="not-found-intro">
        <div class="not-found-copy">
          <p class="section-kicker">РЕЗУЛЬТАТ СКАНИРОВАНИЯ</p>
          <h1>Этого вина пока нет в каталоге</h1>
          <p class="intro-description">Подберём российские вина с похожими характеристиками.</p>
          <NuxtLink to="/scan" class="text-action"><ResultIcon name="scan" />Сканировать ещё раз</NuxtLink>
        </div>
        <div v-if="showPhoto" class="scanned-label"><img :src="photo!" alt="Загруженная этикетка" /><span>Ваша этикетка</span></div>
        <div v-else class="catalog-note"><span class="catalog-note-number">{{ wines.length ? wines.length.toLocaleString('ru-RU') : '—' }}</span><span>вина в каталоге</span><span class="catalog-note-line"/><p>Возможно, ваше новое<br/>любимое — среди них.</p></div>
      </section>

      <div v-if="status === 'pending'" class="result-loading" role="status"><span class="loading-ring" />Загружаем вина…</div>
      <div v-else-if="error" class="result-empty" role="alert"><h2>Каталог временно недоступен</h2><p>Попробуйте загрузить его ещё раз.</p><button class="btn-wine" @click="refresh()">Повторить</button></div>
      <template v-else>
        <section class="matching-panel" aria-labelledby="matching-title">
          <div class="matching-title"><h2 id="matching-title">{{ hasParameters ? 'Подбираем по характеристикам' : 'Каким было ваше вино?' }}</h2><p id="matching-hint">{{ hasParameters ? 'Доступны только совместимые сочетания.' : 'Начните с любой характеристики — остальные варианты подстроятся.' }}</p><button v-if="hasParameters" type="button" class="matching-reset" @click="clear">Сбросить параметры</button><p v-if="adjustedParameters" role="status">Для подбора оставили совместимые характеристики из каталога. Их можно изменить.</p></div>
          <div class="matching-controls" aria-describedby="matching-hint">
            <label for="category">Категория<select id="category" v-model="category" aria-label="Категория"><option value="">Любая категория</option><option v-for="item in filters.categories" :key="item" :value="item">{{ item }}</option></select></label>
            <label for="grape">Виноград<select id="grape" v-model="grape" aria-label="Виноград"><option value="">Любой сорт</option><option v-for="item in filters.grapes" :key="item" :value="item">{{ item }}</option></select></label>
            <label for="region">Регион<select id="region" v-model="region" aria-label="Регион"><option value="">Любой регион</option><option v-for="item in filters.regions" :key="item" :value="item">{{ item }}</option></select></label>
            <label for="dish">Блюдо<select id="dish" v-model="dish" aria-label="Блюдо"><option value="">Любое блюдо</option><option v-for="item in filters.dishes" :key="item" :value="item">{{ item }}</option></select></label>
          </div>
        </section>
        <WineCarousel v-if="recommendations.length" :wines="recommendations" :profile="profile" :catalog-link="catalogLink" title="Похожие вина" :subtitle="subtitle" />
        <div v-else-if="hasParameters" class="recommendation-empty" role="status"><h2>Близких вариантов пока нет</h2><p>Попробуйте другую категорию или уберите часть параметров.</p><button class="btn-wine-outline" @click="clear">Сбросить параметры</button><a :href="catalogLink.href" class="text-action">Посмотреть в полном каталоге<ResultIcon name="arrow" /></a></div>
        <div v-else class="choose-prompt"><ResultIcon name="search" /><p>Выберите характеристики выше,<br/>чтобы увидеть подборку из каталога.</p></div>
        <p v-if="recommendations.length" class="recommendation-disclaimer">Это похожие вина из каталога, а не точное совпадение с вашей этикеткой.</p>
      </template>
    </div>
  </div>
</template>
