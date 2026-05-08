import { apiClient } from '../lib/apiClient'

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
    const { data } = await apiClient.get<UserProfile>(`/users/${userId}`)
    return { data: data ?? null, error: null }
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
    const { data } = await apiClient.put<UserProfile>(`/users/${userId}/xp`, { xpDelta })
    return { data: data ?? null, error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}