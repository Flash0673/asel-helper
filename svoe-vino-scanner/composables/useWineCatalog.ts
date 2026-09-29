import type { WineCard } from '~/types/wine'

export function useWineCatalog() {
  return useAsyncData<WineCard[]>('wine-catalog', () => $fetch('/catalog/wines.json'), { default: () => [] })
}
