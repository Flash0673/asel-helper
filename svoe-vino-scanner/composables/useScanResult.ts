import type { ScanResponse } from '~/types/wine'

export function useScanResult() {
  const result = useState<ScanResponse | null>('scan-result', () => null)
  const photo = useState<string | null>('scan-photo', () => null)
  function setResult(value: ScanResponse, image: string | null = null) {
    if (import.meta.client && photo.value && photo.value !== image) URL.revokeObjectURL(photo.value)
    result.value = value
    photo.value = image
  }
  return { result, photo, setResult }
}
