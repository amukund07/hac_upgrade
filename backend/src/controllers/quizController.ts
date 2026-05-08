import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import type { AuthenticatedRequest } from '../middleware/authMiddleware'
import { getQuizById, getQuizQuestions, submitQuizResult } from '../services/quizService'
import { sendResponse } from '../utils/response'

export const fetchQuizByModule = asyncHandler(async (req: Request, res: Response) => {
  const quiz = await getQuizById(String(req.params.quizId))
  void sendResponse({ res, statusCode: 200, data: quiz })
})

export const fetchQuizQuestions = asyncHandler(async (req: Request, res: Response) => {
  const questions = await getQuizQuestions(String(req.params.quizId))
  void sendResponse({ res, statusCode: 200, data: questions })
})

export const submitQuiz = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const result = await submitQuizResult({
    user_id: String(req.user?.id ?? req.body.user_id),
    quiz_id: String(req.params.quizId),
    score: req.body.score,
    total_questions: req.body.total_questions,
    passed: Boolean(req.body.passed),
  })

  void sendResponse({ res, statusCode: 200, data: result })
})