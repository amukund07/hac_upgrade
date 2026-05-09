/**
 * Embedding Generation Service
 * Generates vector embeddings for knowledge base content using Gemini API
 */

import { GoogleGenerativeAI } from '@google/generative-ai'
import { env } from '../../config/env'

export interface EmbeddingResult {
  text: string
  embedding: number[]
}

// Initialize Gemini AI client
const getAIClient = () => {
  if (!env.geminiApiKey) {
    throw new Error('Gemini API key not configured. Set GEMINI_API_KEY environment variable.')
  }
  return new GoogleGenerativeAI(env.geminiApiKey)
}

/**
 * Generate a single embedding for text
 */
export const generateEmbedding = async (text: string): Promise<number[]> => {
  try {
    const ai = getAIClient()
    
    // Use Gemini's embedding model
    const model = ai.getGenerativeModel({ model: 'embedding-001' })
    const result = await model.embedContent(text)

    // Extract embedding vector from response
    const values = result.embedding?.values
    if (!values || !Array.isArray(values)) {
      throw new Error('No embedding values in response')
    }

    return values
  } catch (error) {
    console.error('Error generating embedding:', error)
    throw error
  }
}

/**
 * Generate embeddings for multiple texts in batch
 * (Note: Gemini API doesn't have native batch, so we call sequentially with delays)
 */
export const generateEmbeddingsBatch = async (
  texts: string[],
  delayMs: number = 100
): Promise<EmbeddingResult[]> => {
  const results: EmbeddingResult[] = []

  for (const text of texts) {
    try {
      const embedding = await generateEmbedding(text)
      results.push({ text, embedding })
      
      // Add delay between requests to avoid rate limiting
      if (texts.indexOf(text) < texts.length - 1) {
        await new Promise((resolve) => setTimeout(resolve, delayMs))
      }
    } catch (error) {
      console.error(`Failed to embed text: "${text.substring(0, 50)}..."`, error)
      // Continue with next text instead of failing completely
      results.push({ text, embedding: [] })
    }
  }

  return results
}

/**
 * Generate embedding for a single query (typically user question)
 */
export const embedQuery = async (query: string): Promise<number[]> => {
  return generateEmbedding(query)
}
