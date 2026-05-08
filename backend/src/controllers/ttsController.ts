import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import { synthesizeText } from '../services/ttsService'
import { sendResponse } from '../utils/response'

export const synthesize = asyncHandler(async (req: Request, res: Response) => {
  const { text } = req.body

  if (!text || typeof text !== 'string') {
    void sendResponse({ res, statusCode: 400, message: 'Missing text in request body' })
    return
  }

  const audioBase64 = await synthesizeText(text)

  void sendResponse({ res, statusCode: 200, data: { audioBase64 } })
})
