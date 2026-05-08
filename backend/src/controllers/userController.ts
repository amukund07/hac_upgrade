import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import type { AuthenticatedRequest } from '../middleware/authMiddleware'
import { getUserProfile, updateUserProfile, updateXP } from '../services/userService'
import { sendResponse } from '../utils/response'

export const fetchUserProfile = asyncHandler(async (req: Request, res: Response) => {
  const user = await getUserProfile(String(req.params.userId))
  void sendResponse({ res, statusCode: 200, data: user })
})

export const updateUserXp = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const user = await updateXP(String(req.params.userId), Number(req.body.xpDelta ?? 0))
  void sendResponse({ res, statusCode: 200, data: user })
})

export const patchUserProfile = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const user = await updateUserProfile(String(req.params.userId), req.body)
  void sendResponse({ res, statusCode: 200, data: { user } })
})