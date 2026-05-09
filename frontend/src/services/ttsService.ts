import { apiClient } from '../lib/apiClient'
import { unwrapApiData } from './apiEnvelope'

export interface TtsRequest {
  text: string
  style?: 'story' | 'lesson' | 'chat'
}

export interface TtsResponse {
  audioBase64: string
  fallback?: 'browser' | 'gemini'
}

type ServiceResult<T> = Promise<{ data: T | null; error: string | null }>

const mapError = (error: unknown): string => (error instanceof Error ? error.message : 'An unexpected error occurred.')

export const synthesizeNarration = async (payload: TtsRequest): ServiceResult<TtsResponse> => {
  try {
    const response = await apiClient.post('/tts', payload)
    return { data: unwrapApiData<TtsResponse>(response), error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}