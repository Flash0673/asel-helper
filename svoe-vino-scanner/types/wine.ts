export interface WineCard {
  slug: string
  name: string
  winery: string
  region: string
  category: string
  color: string
  vintage: number | null
  description: string
  rating: number | null
  image: string
  sourceImage: string
  temperature: string
  strength: string
  grapes: string[]
  foodPairing: string[]
  url: string
  similarSlugs: string[]
  similarTitles: string
  similarUrls: string[]
}

/** Characteristics actually returned by the recognizer or chosen by the user. */
export interface WineProfile {
  category?: string
  grapes?: string[]
  region?: string
  vintage?: number | null
  dish?: string
}

export interface ScanResponse {
  found: boolean
  confidence?: { top1: number; top5?: number }
  wine?: { slug: string }
  profile?: WineProfile
  demo?: boolean
}
