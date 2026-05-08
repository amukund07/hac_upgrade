import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import type { AuthenticatedRequest } from '../middleware/authMiddleware'
import { completeLesson, getLessonById, getUserLessonProgress } from '../services/lessonService'
import { sendResponse } from '../utils/response'

export const fetchLesson = asyncHandler(async (req: Request, res: Response) => {
  const lesson = await getLessonById(String(req.params.id))
  void sendResponse({ res, statusCode: 200, data: lesson })
})

export const completeLessonController = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const userId = req.user?.id ?? req.body.user_id
  const progress = await completeLesson(String(userId), String(req.params.id))
  void sendResponse({ res, statusCode: 200, data: progress })
})

export const fetchUserLessonProgress = asyncHandler(async (req: Request, res: Response) => {
  const progress = await getUserLessonProgress(String(req.params.userId), String(req.params.lessonId))
  void sendResponse({ res, statusCode: 200, data: progress })
})