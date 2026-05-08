import { apiClient } from '../lib/apiClient'

export interface UserModuleProgress {
  id?: string
  user_id: string
  module_id: string
  progress_percentage: number
  completed_lessons_count?: number
  total_lessons_count?: number
  completed_at?: string | null
  updated_at?: string
  created_at?: string
}

type ServiceResult<T> = Promise<{ data: T | null; error: string | null }>

const mapError = (error: unknown): string =>
  error instanceof Error ? error.message : 'An unexpected error occurred.'

// Returns the current progress for a user on a module.
export const getUserModuleProgress = async (
  userId: string,
  moduleId: string,
): ServiceResult<UserModuleProgress> => {
  try {
    const { data } = await apiClient.get<UserModuleProgress>(`/progress/users/${userId}/modules/${moduleId}/progress`)
    return { data: data ?? null, error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}

// Creates or updates the module progress percentage for a user.
export const updateModuleProgress = async (
  progress: UserModuleProgress,
): ServiceResult<UserModuleProgress> => {
  try {
    const { data } = await apiClient.put<UserModuleProgress>(`/progress/users/${progress.user_id}/modules/${progress.module_id}/progress`, progress)
    return { data: data ?? null, error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}