import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import type { AuthenticatedRequest } from '../middleware/authMiddleware'
import { registerUser, loginUser, getCurrentUser, updateCurrentUser } from '../services/authService'
import { validateLoginInput, validateRegisterInput } from '../validators/authValidators'
import { sendResponse } from '../utils/response'

export const register = asyncHandler(async (req: Request, res: Response) => {
  validateRegisterInput(req.body)
  const result = await registerUser(req.body)
  void sendResponse({ res, statusCode: 201, data: result })
})

export const login = asyncHandler(async (req: Request, res: Response) => {
  validateLoginInput(req.body)
  const result = await loginUser(req.body)
  void sendResponse({ res, statusCode: 200, data: result })
})

export const currentUser = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const userId = req.user?.id
  const user = await getCurrentUser(userId ?? '')
  void sendResponse({ res, statusCode: 200, data: { user } })
})

export const logout = asyncHandler(async (_req: AuthenticatedRequest, res: Response) => {
  void sendResponse({ res, statusCode: 200, message: 'Logged out successfully' })
})

export const updateMe = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const userId = req.user?.id
  const user = await updateCurrentUser(userId ?? '', req.body)
  void sendResponse({ res, statusCode: 200, data: { user } })
})