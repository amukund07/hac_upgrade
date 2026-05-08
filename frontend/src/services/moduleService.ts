import { apiClient } from '../lib/apiClient'

export interface LearningModule {
  id: string
  slug?: string
  title: string
  description: string
  difficulty: string
  xp_reward: number
  category?: string
  estimated_time?: string
  hero_story?: string
  created_at?: string
  updated_at?: string
}

export interface Lesson {
  id: string
  module_id: string
  title: string
  content: string
  order_index?: number
  created_at?: string
  updated_at?: string
}

export interface Quiz {
  id: string
  module_id: string
  title: string
  passing_score?: number
  created_at?: string
  updated_at?: string
}

type ServiceResult<T> = Promise<{ data: T | null; error: string | null }>

const mapError = (error: unknown): string =>
  error instanceof Error ? error.message : 'An unexpected error occurred.'

// Fetches every learning module for the home page module list.
export const getAllModules = async (): ServiceResult<LearningModule[]> => {
  try {
    const { data } = await apiClient.get<LearningModule[]>('/modules')
    return { data: data ?? [], error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}

// Fetches a single module by id for the module details page.
export const getModuleById = async (moduleId: string): ServiceResult<LearningModule> => {
  try {
    const { data } = await apiClient.get<LearningModule>(`/modules/${moduleId}`)
    return { data: data ?? null, error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}

// Fetches all lessons that belong to a module.
export const getModuleLessons = async (moduleId: string): ServiceResult<Lesson[]> => {
  try {
    const { data } = await apiClient.get<Lesson[]>(`/modules/${moduleId}/lessons`)
    return { data: data ?? [], error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}

// Fetches all quizzes that belong to a module.
export const getModuleQuizzes = async (moduleId: string): ServiceResult<Quiz[]> => {
  try {
    const { data } = await apiClient.get<Quiz[]>(`/modules/${moduleId}/quizzes`)
    return { data: data ?? [], error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}