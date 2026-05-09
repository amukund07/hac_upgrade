import { QuizModel } from '../models/Quiz'
import { QuizQuestionModel } from '../models/QuizQuestion'
import { UserQuizResultModel } from '../models/UserQuizResult'
import { ApiError } from '../utils/errors'
import { serializeDocument, serializeCollection } from '../utils/serializers'
import { incrementUserXP } from './authService'
import { recalculateModuleProgress } from './progressService'

export const getQuizQuestions = async (quizId: string) => {
  const questions = await QuizQuestionModel.find({ quiz_id: quizId }).sort({ order_index: 1 })
  return serializeCollection(questions)
}

export const getQuizById = async (quizId: string) => {
  const quiz = await QuizModel.findById(quizId)

  if (!quiz) {
    throw new ApiError(404, 'Quiz not found')
  }

  return serializeDocument(quiz)
}

export const submitQuizResult = async (payload: {
  user_id: string
  quiz_id: string
  score: number
  total_questions: number
  passed: boolean
}) => {
  const result = await UserQuizResultModel.create(payload)
  const totalQuestions = Math.max(1, payload.total_questions)
  const earnedXp = Math.max(0, Math.round((payload.score / totalQuestions) * 200))

  if (earnedXp > 0) {
    await incrementUserXP(payload.user_id, earnedXp)
  }

  // Recalculate module progress if the quiz is linked to a module
  const quiz = await QuizModel.findById(payload.quiz_id)
  if (quiz && quiz.module_id) {
    await recalculateModuleProgress(payload.user_id, String(quiz.module_id))
  }

  return {
    ...serializeDocument(result),
    earned_xp: earnedXp,
  }
}