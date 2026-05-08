import { apiClient } from '../lib/apiClient'

export interface Lesson {
  id: string
  module_id: string
  title: string
  content: string
  order_index?: number
  created_at?: string
  updated_at?: string
}

export interface UserLessonProgress {
  id?: string
  user_id: string
  lesson_id: string
  completed: boolean
  completed_at?: string | null
  progress_percentage?: number
  created_at?: string
  updated_at?: string
}

type ServiceResult<T> = Promise<{ data: T | null; error: string | null }>

const mapError = (error: unknown): string =>
  error instanceof Error ? error.message : 'An unexpected error occurred.'

// Fetches a lesson and its content by lesson id.
export const getLessonById = async (lessonId: string): ServiceResult<Lesson> => {
  try {
    const { data } = await apiClient.get<Lesson>(`/lessons/${lessonId}`)
    return { data: data ?? null, error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}

// Marks a lesson as completed for a specific user and updates the completion timestamp.
export const completeLesson = async (
  userId: string,
  lessonId: string,
): ServiceResult<UserLessonProgress> => {
  try {
    const payload: UserLessonProgress = {
      user_id: userId,
      lesson_id: lessonId,
      completed: true,
      completed_at: new Date().toISOString(),
      progress_percentage: 100,
    }

    const { data } = await apiClient.post<UserLessonProgress>(`/lessons/${lessonId}/complete`, payload)
    return { data: data ?? null, error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}

// Returns the tracked lesson progress for a user and lesson.
export const getUserLessonProgress = async (
  userId: string,
  lessonId: string,
): ServiceResult<UserLessonProgress> => {
  try {
    const { data } = await apiClient.get<UserLessonProgress>(`/progress/users/${userId}/lessons/${lessonId}/progress`)
    return { data: data ?? null, error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}