import source from '../data/catalogFilters.json'
import type { WineProfile } from '../types/wine'

const normalize = (value: string) => value.toLocaleLowerCase('ru').replace(/ё/g, 'е').replace(/[-–—\s]+/g, ' ').trim()
type FilterKey = keyof typeof source.filters

/** URL keys and values are the public catalogue's actual filter identifiers. */
export function buildCatalogLink(profile: WineProfile = {}) {
  const query = new URLSearchParams()
  const applied: string[] = []
  const unsupported: string[] = []
  function add(key: FilterKey, label?: string) {
    if (!label) return
    const options = source.filters[key]
    const option = options.find(item => item.name === label) ?? options.find(item => normalize(item.name) === normalize(label))
    if (option) { query.append(key, option.value); applied.push(option.name) }
    else unsupported.push(label)
  }
  if (profile.category) {
    const [color, ...sweetness] = profile.category.split(' ')
    add('colors', color)
    add('sweetness', sweetness.join(' '))
  }
  for (const grape of [...new Set(profile.grapes ?? [])]) add('grapes', grape)
  add('regions', profile.region)
  add('dishes', profile.dish)
  // The public catalogue has no vintage filter. Never invent a query parameter.
  if (profile.vintage) unsupported.push(`год ${profile.vintage}`)
  return {
    href: `https://vino-svoe.ru/wines${query.size ? `?${query.toString()}` : ''}`,
    applied,
    unsupported,
  }
}
