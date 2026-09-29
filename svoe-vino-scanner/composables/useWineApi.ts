import type { ScanResponse } from '~/types/wine'
import { DEMO_PROFILE, DEMO_WINE_SLUG } from '~/utils/wineCatalog'

export function useWineApi() {
  const config = useRuntimeConfig()
  const useMock = String(config.public.useMock) !== 'false'

  async function scanWine(
    form: FormData,
    onProgress?: (p: number) => void,
    scenario: 'found' | 'not-found' = 'found'
  ): Promise<ScanResponse> {
    if (useMock) {
      for (let p = 15; p <= 85; p += 20) {
        await new Promise((r) => setTimeout(r, 200))
        onProgress?.(p)
      }
      await new Promise((r) => setTimeout(r, 300))
      onProgress?.(100)

      return scenario === 'found'
        ? { found: true, wine: { slug: DEMO_WINE_SLUG }, demo: true }
        : { found: false, profile: { ...DEMO_PROFILE }, demo: true }
    }

    return await $fetch<ScanResponse>(`${config.public.apiBase}/api/scan`, {
      method: 'POST',
      body: form,
      timeout: 30000
    })
  }

  return { scanWine, useMock }
}
