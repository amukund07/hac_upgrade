import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import { generateGeminiResponse } from '../services/geminiService'
import { sendResponse } from '../utils/response'

export const handleGeminiRequest = asyncHandler(async (req: Request, res: Response) => {
  const { type, question, contextSnippets, title, content } = req.body

  if (!type) {
    void sendResponse({ res, statusCode: 400, message: 'Missing type in request body' })
    return
  }

  const response = await generateGeminiResponse(type, { question, contextSnippets, title, content })

  void sendResponse({ res, statusCode: 200, data: { response } })
})
