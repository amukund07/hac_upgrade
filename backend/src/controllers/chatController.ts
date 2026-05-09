import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import { generateChatResponse } from '../services/chatService'
import { sendResponse } from '../utils/response'

export const chat = asyncHandler(async (req: Request, res: Response) => {
  const { question, contextSnippets } = req.body

  if (!question || typeof question !== 'string') {
    void sendResponse({ res, statusCode: 400, message: 'Missing question in request body' })
    return
  }

  const response = await generateChatResponse(question, contextSnippets)

  void sendResponse({ res, statusCode: 200, data: { response } })
})
