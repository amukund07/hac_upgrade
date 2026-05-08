import { apiClient } from '../lib/apiClient'
import { unwrapApiData } from './apiEnvelope'

export interface UserProfile {
  id: string
  name: string
  email: string
  avatar_url?: string | null
  xp_points: number
  level: number
  streak?: number
  created_at?: string
  updated_at?: string
}

type ServiceResult<T> = Promise<{ data: T | null; error: string | null }>

const mapError = (error: unknown): string =>
  error instanceof Error ? error.message : 'An unexpected error occurred.'

// Fetches a user profile by id.
export const getUserProfile = async (userId: string): ServiceResult<UserProfile> => {
  try {
    const response = await apiClient.get(`/users/${userId}`)
    return { data: unwrapApiData<UserProfile>(response), error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}

// Adds XP to a user profile and returns the updated row.
export const updateXP = async (
  userId: string,
  xpDelta: number,
): ServiceResult<UserProfile> => {
  try {
    const response = await apiClient.put(`/users/${userId}/xp`, { xpDelta })
    return { data: unwrapApiData<UserProfile>(response), error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}