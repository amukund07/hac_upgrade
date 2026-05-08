import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import type { AuthenticatedRequest } from '../middleware/authMiddleware'
import { getAchievements, getUserAchievements, unlockAchievement } from '../services/achievementService'
import { sendResponse } from '../utils/response'

export const fetchAchievements = asyncHandler(async (_req: Request, res: Response) => {
  const achievements = await getAchievements()
  void sendResponse({ res, statusCode: 200, data: achievements })
})

export const fetchUserAchievements = asyncHandler(async (req: Request, res: Response) => {
  const achievements = await getUserAchievements(String(req.params.userId))
  void sendResponse({ res, statusCode: 200, data: achievements })
})

export const unlockAchievementController = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const userId = String(req.user?.id ?? req.body.user_id)
  const achievement = await unlockAchievement({
    user_id: userId,
    achievement_id: String(req.body.achievement_id),
    unlocked_at: new Date(req.body.unlocked_at ?? Date.now()),
  })

  void sendResponse({ res, statusCode: 200, data: achievement })
})