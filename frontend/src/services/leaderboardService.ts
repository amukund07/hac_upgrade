import { apiClient } from '../lib/apiClient'
import { unwrapApiData } from './apiEnvelope'

export interface LeaderboardEntry {
  id: string
  name: string
  avatar_url?: string | null
  xp_points: number
  level?: number
  streak?: number
}

type ServiceResult<T> = Promise<{ data: T | null; error: string | null }>

const mapError = (error: unknown): string =>
  error instanceof Error ? error.message : 'An unexpected error occurred.'

// Fetches the leaderboard ordered by the highest XP totals.
export const getLeaderboard = async (): ServiceResult<LeaderboardEntry[]> => {
  try {
    const response = await apiClient.get('/leaderboard')
    return { data: unwrapApiData<LeaderboardEntry[]>(response) ?? [], error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}