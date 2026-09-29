import type { WineCard, WineProfile } from '../types/wine'

export const DEMO_WINE_SLUG = 'cantiani-cabernet-sauvignon-reserve-2024'
export const DEMO_PROFILE: WineProfile = { category: 'Красное сухое', grapes: ['Каберне Совиньон'], dish: 'Мясо и стейки' }
const normalize = (value: string) => value.toLocaleLowerCase('ru').replace(/ё/g, 'е').replace(/[-–—\s]+/g, ' ').trim()

export function wineMatches(wine: WineCard, profile: WineProfile): string[] {
  const reasons: string[] = []
  if (profile.category && normalize(wine.category) === normalize(profile.category)) reasons.push(wine.category)
  if (profile.grapes?.some(grape => wine.grapes.some(other => normalize(other) === normalize(grape)))) reasons.push('Тот же сорт')
  if (profile.region && normalize(wine.region) === normalize(profile.region)) reasons.push(wine.region)
  if (profile.vintage && wine.vintage === profile.vintage) reasons.push(String(wine.vintage))
  if (profile.dish && wine.foodPairing.some(dish => normalize(dish) === normalize(profile.dish!))) reasons.push('К выбранному блюду')
  return reasons
}

/** The same predicate powers recommendations and the dependent filter options. */
export function filterWines(wines: WineCard[], profile: WineProfile): WineCard[] {
  return wines.filter(wine =>
    (!profile.category || normalize(wine.category) === normalize(profile.category)) &&
    (!profile.grapes?.length || wine.grapes.some(grape => profile.grapes!.some(other => normalize(grape) === normalize(other)))) &&
    (!profile.region || normalize(wine.region) === normalize(profile.region)) &&
    (!profile.dish || wine.foodPairing.some(dish => normalize(dish) === normalize(profile.dish!)))
  )
}

const uniqueValues = (values: string[]) => [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b, 'ru'))

/** Each list respects every other selection, allowing the current field to change. */
export function availableWineFilters(wines: WineCard[], profile: WineProfile) {
  return {
    categories: uniqueValues(filterWines(wines, { ...profile, category: undefined }).map(wine => wine.category)),
    grapes: uniqueValues(filterWines(wines, { ...profile, grapes: undefined }).flatMap(wine => wine.grapes)),
    regions: uniqueValues(filterWines(wines, { ...profile, region: undefined }).map(wine => wine.region)),
    dishes: uniqueValues(filterWines(wines, { ...profile, dish: undefined }).flatMap(wine => wine.foodPairing)),
  }
}

/** A recognizer can return a combination absent from the catalog; retain a compatible subset. */
export function reconcileWineProfile(wines: WineCard[], profile: WineProfile) {
  const compatible: WineProfile = { vintage: profile.vintage }
  const removed: string[] = []
  const resolve = (value: string | undefined, options: string[]) => {
    if (!value) return undefined
    const match = options.find(option => normalize(option) === normalize(value))
    if (!match) removed.push(value)
    return match
  }
  compatible.category = resolve(profile.category, uniqueValues(wines.map(wine => wine.category)))
  compatible.grapes = (profile.grapes ?? []).map(grape => resolve(grape, uniqueValues(filterWines(wines, compatible).flatMap(wine => wine.grapes)))).filter((grape): grape is string => Boolean(grape))
  compatible.region = resolve(profile.region, uniqueValues(filterWines(wines, compatible).map(wine => wine.region)))
  compatible.dish = resolve(profile.dish, uniqueValues(filterWines(wines, compatible).flatMap(wine => wine.foodPairing)))
  return { profile: compatible, removed }
}

/** Selected characteristics narrow the candidates; vintage and rating rank matches. */
export function recommendWines(wines: WineCard[], profile: WineProfile, limit = 12): WineCard[] {
  if (!profile.category && !profile.grapes?.length && !profile.region && !profile.vintage && !profile.dish) return []
  return filterWines(wines, profile)
    .map(wine => {
      let score = 0
      if (profile.category && normalize(wine.category) === normalize(profile.category)) score += 100
      if (profile.grapes?.length) score += wine.grapes.filter(grape => profile.grapes!.some(other => normalize(grape) === normalize(other))).length * 30
      if (profile.region && normalize(wine.region) === normalize(profile.region)) score += 15
      if (profile.vintage && wine.vintage === profile.vintage) score += 5
      if (profile.dish) score += 20
      return { wine, score }
    })
    .filter(item => item.score > 0)
    .sort((a, b) => b.score - a.score || (b.wine.rating ?? -1) - (a.wine.rating ?? -1) || a.wine.name.localeCompare(b.wine.name, 'ru'))
    .slice(0, limit).map(item => item.wine)
}
