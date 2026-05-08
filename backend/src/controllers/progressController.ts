import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import type { AuthenticatedRequest } from '../middleware/authMiddleware'
import { getUserLessonProgress, getUserModuleProgress, recalculateModuleProgress, updateModuleProgress } from '../services/progressService'
import { sendResponse } from '../utils/response'

export const fetchUserModuleProgress = asyncHandler(async (req: Request, res: Response) => {
  const progress = await getUserModuleProgress(String(req.params.userId), String(req.params.moduleId))
  void sendResponse({ res, statusCode: 200, data: progress })
})

export const updateUserModuleProgress = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const userId = String(req.user?.id ?? req.body.user_id)
  const progress = await updateModuleProgress({
    user_id: userId,
    module_id: String(req.params.moduleId),
    progress_percentage: req.body.progress_percentage,
    completed_lessons_count: req.body.completed_lessons_count,
    total_lessons_count: req.body.total_lessons_count,
    completed_at: req.body.completed_at,
  })

  void sendResponse({ res, statusCode: 200, data: progress })
})

export const fetchUserLessonProgressController = asyncHandler(async (req: Request, res: Response) => {
  const progress = await getUserLessonProgress(String(req.params.userId), String(req.params.lessonId))
  void sendResponse({ res, statusCode: 200, data: progress })
})

export const recalculateProgress = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const userId = String(req.user?.id ?? req.params.userId)
  const progress = await recalculateModuleProgress(userId, String(req.params.moduleId))
  void sendResponse({ res, statusCode: 200, data: progress })
})