export type ApiEnvelope<T> = {
  success: boolean
  message?: string
  data?: T
}

export const unwrapApiData = <T>(response: { data: ApiEnvelope<T> | T }): T | null => {
  const payload = response.data

  if (payload && typeof payload === 'object' && 'success' in payload && 'data' in payload) {
    return (payload as ApiEnvelope<T>).data ?? null
  }

  return (payload as T) ?? null
}

export const unwrapApiCollection = <T>(response: { data: ApiEnvelope<T[]> | T[] | T | null | undefined }): T[] => {
  const payload = unwrapApiData<unknown>(response)

  return Array.isArray(payload) ? (payload as T[]) : []
}