import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import { generateGeminiResponse } from '../services/geminiService'
import { sendResponse } from '../utils/response'

const fallbackResponseByType = {
  chat: 'I could not reach the AI service right now. Please try again in a moment.',
  rag: 'I could not complete context generation right now. Please retry your question in a few seconds.',
  narration: 'This lesson highlights traditional wisdom, practical observation, and learning through lived experience.',
} as const

type GeminiRequestType = keyof typeof fallbackResponseByType

export const handleGeminiRequest = asyncHandler(async (req: Request, res: Response) => {
  const { type, question, contextSnippets, title, content } = req.body

  if (!type) {
    void sendResponse({ res, statusCode: 400, message: 'Missing type in request body' })
    return
  }

  if (type !== 'chat' && type !== 'rag' && type !== 'narration') {
    void sendResponse({ res, statusCode: 400, message: 'Invalid type. Use chat, rag, or narration.' })
    return
  }

  const requestType = type as GeminiRequestType

  let response: string = fallbackResponseByType[requestType]

  try {
    response = await generateGeminiResponse(requestType, { question, contextSnippets, title, content })
  } catch (error) {
    console.error('Gemini request failed in controller:', error)
  }

  void sendResponse({ res, statusCode: 200, data: { response } })
})
