import { apiClient } from '../lib/apiClient'

export interface Quiz {
  id: string
  module_id: string
  title: string
  passing_score?: number
  created_at?: string
  updated_at?: string
}

export interface QuizQuestion {
  id: string
  quiz_id: string
  question: string
  options?: string[] | null
  correct_answer?: string
  order_index?: number
  created_at?: string
  updated_at?: string
}

export interface QuizResult {
  id?: string
  user_id: string
  quiz_id: string
  score: number
  total_questions: number
  passed: boolean
  created_at?: string
  updated_at?: string
}

export interface QuizSubmissionResult extends QuizResult {
  earned_xp?: number
}

type ServiceResult<T> = Promise<{ data: T | null; error: string | null }>

const mapError = (error: unknown): string =>
  error instanceof Error ? error.message : 'An unexpected error occurred.'

// Fetches the quiz record attached to a module.
export const getQuizByModule = async (moduleId: string): ServiceResult<Quiz> => {
  try {
    const { data } = await apiClient.get<Quiz>(`/modules/${moduleId}/quiz`)
    return { data: data ?? null, error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}

// Fetches the questions for a quiz in display order.
export const getQuizQuestions = async (quizId: string): ServiceResult<QuizQuestion[]> => {
  try {
    const { data } = await apiClient.get<QuizQuestion[]>(`/quizzes/${quizId}/questions`)
    return { data: data ?? [], error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}

// Stores a quiz attempt and whether the user passed.
export const submitQuizResult = async (
  result: QuizResult,
): ServiceResult<QuizSubmissionResult> => {
  try {
    const { data } = await apiClient.post<QuizSubmissionResult>(`/quizzes/${result.quiz_id}/submit`, result)
    return { data: data ?? null, error: null }
  } catch (error) {
    return { data: null, error: mapError(error) }
  }
}