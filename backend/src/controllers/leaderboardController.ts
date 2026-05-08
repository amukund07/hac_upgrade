import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import { getLeaderboard } from '../services/leaderboardService'
import { sendResponse } from '../utils/response'

export const fetchLeaderboard = asyncHandler(async (_req: Request, res: Response) => {
  const leaderboard = await getLeaderboard()
  void sendResponse({ res, statusCode: 200, data: leaderboard })
})