/**
 * RAG Chat Service
 * Complete pipeline: query embedding -> retrieval -> Gemini generation -> history storage
 */

import { v4 as uuidv4 } from 'uuid'
import { GoogleGenerativeAI } from '@google/generative-ai'
import { env } from '../../config/env'
import { embedQuery } from '../embeddings/embeddingService'
import { searchSimilarContent, formatRetrievedSources } from './retrieval'
import {
  buildContextInjectionPrompt,
  buildFallbackPrompt,
  buildErrorRecoveryPrompt,
} from '../prompts/ragPrompts'
import { ChatHistory, IChatHistory } from '../../models/ChatHistory'

export interface RAGChatOptions {
  userId?: string
  sessionId?: string
  domain?: string
  topK?: number
  similarityThreshold?: number
}

export interface RAGChatResponse {
  response: string
  sources: Array<{
    title: string
    domain: string
    similarity: number
  }>
  responseTime: number
  sessionId: string
}

/**
 * Main RAG chat pipeline
 */
export const generateRAGChatResponse = async (
  userQuery: string,
  options: RAGChatOptions = {}
): Promise<RAGChatResponse> => {
  if (!userQuery || userQuery.trim().length === 0) {
    throw new Error('User query cannot be empty')
  }

  const startTime = Date.now()
  const sessionId = options.sessionId || uuidv4()

  try {
    // Step 1: Generate embedding for the user query
    console.log('[RAG] Generating query embedding...')
    const queryEmbedding = await embedQuery(userQuery)

    // Step 2: Retrieve similar content from knowledge base
    console.log('[RAG] Searching for similar content...')
    const retrievedResults = await searchSimilarContent(queryEmbedding, {
      topK: options.topK || 5,
      similarityThreshold: options.similarityThreshold || 0.3,
      domain: options.domain,
    })

    const retrievedSources = formatRetrievedSources(retrievedResults)

    // Step 3: Build prompt with context
    let systemPrompt: string
    let userPrompt: string

    if (retrievedResults.length > 0) {
      console.log(
        `[RAG] Found ${retrievedResults.length} relevant sources, generating answer...`
      )
      const promptData = buildContextInjectionPrompt(userQuery, retrievedSources, false)
      systemPrompt = promptData.system
      userPrompt = promptData.user
    } else {
      console.log('[RAG] No relevant sources found, using fallback approach...')
      const fallbackPrompt = buildFallbackPrompt(userQuery)
      systemPrompt = fallbackPrompt
      userPrompt = userQuery
    }

    // Step 4: Generate response using Gemini
    console.log('[RAG] Calling Gemini API...')
    const response = await generateGeminiResponseWithPrompts(systemPrompt, userPrompt)

    const responseTime = Date.now() - startTime

    // Step 5: Store chat history
    try {
      await storeChatHistory({
        userId: options.userId,
        sessionId,
        query: userQuery,
        response,
        retrievedSources,
        responseTime,
      })
    } catch (historyError) {
      console.error('[RAG] Failed to store chat history:', historyError)
      // Don't fail the response if history storage fails
    }

    return {
      response,
      sources: retrievedSources.map((source) => ({
        title: source.title,
        domain: source.domain,
        similarity: source.similarity,
      })),
      responseTime,
      sessionId,
    }
  } catch (error) {
    console.error('[RAG] Error in RAG pipeline:', error)
    
    // Attempt error recovery
    try {
      const errorPrompt = buildErrorRecoveryPrompt(userQuery, error instanceof Error ? error.message : 'Unknown error')
      const response = await generateGeminiResponseWithPrompts(errorPrompt.system, errorPrompt.user)
      const responseTime = Date.now() - startTime

      return {
        response,
        sources: [],
        responseTime,
        sessionId,
      }
    } catch (recoveryError) {
      console.error('[RAG] Error recovery failed:', recoveryError)
      throw error
    }
  }
}

/**
 * Models to try for chat generation
 */
const CHAT_MODELS = [
  'gemini-2.0-flash',
  'gemini-1.5-flash',
  'gemini-1.5-pro',
]

/**
 * Generate response from Gemini with given prompts
 */
const generateGeminiResponseWithPrompts = async (
  systemPrompt: string,
  userPrompt: string
): Promise<string> => {
  if (!env.geminiApiKey) {
    throw new Error('Gemini API key not configured')
  }

  const ai = new GoogleGenerativeAI(env.geminiApiKey)
  let lastError: any = null

  for (const modelId of CHAT_MODELS) {
    try {
      console.log(`[RAG] Attempting generation with model: ${modelId}`)
      const model = ai.getGenerativeModel({ model: modelId })
      
      const result = await model.generateContent(`${systemPrompt}\n\n${userPrompt}`)
      const text = result.response.text()

      if (text) {
        console.log(`[RAG] ✓ Successfully generated response with model: ${modelId}`)
        return text
      }
    } catch (error: any) {
      const errorMsg = error?.message || String(error)
      const statusCode = error?.status || 500
      
      console.warn(`[RAG] Gemini generation error with ${modelId}: ${errorMsg} (Status: ${statusCode})`)
      lastError = error

      // If it's a permanent error (Auth/Permission), don't bother with other models
      if (statusCode === 401 || statusCode === 403) {
        console.error(`[RAG] Permanent error hit with ${modelId}, stopping fallback.`)
        break
      }
      
      // For rate limits (429) or transient errors (500), try the next model
      console.log(`[RAG] Error with ${modelId}, trying next model in list...`)
    }
  }

  throw lastError || new Error('All Gemini models failed to generate a response')
}

/**
 * Store chat interaction in database for history
 */
const storeChatHistory = async (data: {
  userId?: string
  sessionId: string
  query: string
  response: string
  retrievedSources: Array<{
    title: string
    content: string
    domain: string
    similarity: number
  }>
  responseTime: number
}): Promise<IChatHistory> => {
  try {
    const chatRecord = new ChatHistory({
      userId: data.userId,
      sessionId: data.sessionId,
      query: data.query,
      response: data.response,
      retrievedSources: data.retrievedSources,
      modelUsed: 'gemini-2.0-flash',
      responseTime: data.responseTime,
    })

    await chatRecord.save()
    return chatRecord
  } catch (error) {
    console.error('Error storing chat history:', error)
    throw error
  }
}

/**
 * Retrieve chat history for a session
 */
export const getChatHistory = async (
  sessionId: string,
  limit: number = 50
): Promise<any[]> => {
  try {
    return await ChatHistory.find({ sessionId })
      .sort({ createdAt: -1 })
      .limit(limit)
      .lean()
      .exec()
  } catch (error) {
    console.error('Error retrieving chat history:', error)
    throw error
  }
}

/**
 * Retrieve user's chat sessions
 */
export const getUserChatSessions = async (
  userId: string,
  limit: number = 20
): Promise<
  Array<{
    sessionId: string
    lastMessage: string
    timestamp: Date
    messageCount: number
  }>
> => {
  try {
    const sessions = await ChatHistory.aggregate([
      { $match: { userId } },
      {
        $group: {
          _id: '$sessionId',
          lastMessage: { $last: '$response' },
          timestamp: { $max: '$createdAt' },
          messageCount: { $sum: 1 },
        },
      },
      { $sort: { timestamp: -1 } },
      { $limit: limit },
      {
        $project: {
          sessionId: '$_id',
          lastMessage: 1,
          timestamp: 1,
          messageCount: 1,
          _id: 0,
        },
      },
    ])

    return sessions
  } catch (error) {
    console.error('Error retrieving user chat sessions:', error)
    throw error
  }
}

/**
 * Clear chat history for cleanup
 */
export const clearChatHistory = async (sessionId: string): Promise<void> => {
  try {
    await ChatHistory.deleteMany({ sessionId })
  } catch (error) {
    console.error('Error clearing chat history:', error)
    throw error
  }
}
