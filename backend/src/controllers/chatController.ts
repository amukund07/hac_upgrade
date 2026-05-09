import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import { generateRAGChatResponse, getChatHistory } from '../ai/rag/ragChatService'
import { sendResponse } from '../utils/response'

/**
 * POST /api/chat/query
 * Main RAG chat endpoint
 * Receives user query, retrieves context, generates response
 */
export const chat = asyncHandler(async (req: Request, res: Response) => {
  const { query, userId, sessionId, domain } = req.body

  if (!query || typeof query !== 'string') {
    void sendResponse({ res, statusCode: 400, message: 'Missing or invalid query in request body' })
    return
  }

  if (query.trim().length === 0) {
    void sendResponse({ res, statusCode: 400, message: 'Query cannot be empty' })
    return
  }

  try {
    const response = await generateRAGChatResponse(query, {
      userId,
      sessionId,
      domain,
      topK: 5,
      similarityThreshold: 0.3,
    })

    void sendResponse({
      res,
      statusCode: 200,
      data: {
        response: response.response,
        sources: response.sources,
        sessionId: response.sessionId,
        responseTime: response.responseTime,
      },
    })
  } catch (error: any) {
    // eslint-disable-next-line no-console
    console.error('[CHAT CONTROLLER ERROR]:', error)
    
    const message = error?.message || 'Failed to generate response. Please try again.'
    const status = error?.status || 500
    
    void sendResponse({
      res,
      statusCode: status,
      message,
      data: { 
        error: error instanceof Error ? error.stack : String(error)
      }
    })
  }
})

/**
 * GET /api/chat/history/:sessionId
 * Retrieve chat history for a session
 */
export const getChatHistoryHandler = asyncHandler(async (req: Request, res: Response) => {
  const { sessionId } = req.params
  const { limit = '50' } = req.query

  if (!sessionId) {
    void sendResponse({ res, statusCode: 400, message: 'Session ID is required' })
    return
  }

  try {
    const limitNum = Math.min(parseInt(limit as string) || 50, 200)
    const history = await getChatHistory(Array.isArray(sessionId) ? sessionId[0] : sessionId, limitNum)

    void sendResponse({
      res,
      statusCode: 200,
      data: {
        history,
        count: history.length,
      },
    })
  } catch (error) {
    console.error('History retrieval error:', error)
    void sendResponse({
      res,
      statusCode: 500,
      message: 'Failed to retrieve chat history.',
    })
  }
})
