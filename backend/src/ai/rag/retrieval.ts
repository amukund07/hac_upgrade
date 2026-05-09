/**
 * Vector Similarity Search Service
 * Performs semantic search on embedded knowledge using cosine similarity
 */

import { KnowledgeEmbedding, IKnowledgeEmbedding } from '../../models/KnowledgeEmbedding'
import { IRetrievedSource } from '../../models/ChatHistory'

/**
 * Calculate cosine similarity between two vectors
 */
export const cosineSimilarity = (vecA: number[], vecB: number[]): number => {
  if (vecA.length === 0 || vecB.length === 0) {
    return 0
  }

  if (vecA.length !== vecB.length) {
    console.warn('Vector length mismatch in cosine similarity calculation')
    return 0
  }

  let dotProduct = 0
  let magnitudeA = 0
  let magnitudeB = 0

  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i]
    magnitudeA += vecA[i] * vecA[i]
    magnitudeB += vecB[i] * vecB[i]
  }

  magnitudeA = Math.sqrt(magnitudeA)
  magnitudeB = Math.sqrt(magnitudeB)

  if (magnitudeA === 0 || magnitudeB === 0) {
    return 0
  }

  return dotProduct / (magnitudeA * magnitudeB)
}

export interface SearchResult extends IKnowledgeEmbedding {
  similarity: number
}

export interface SearchOptions {
  topK?: number
  similarityThreshold?: number
  domain?: string
  contentType?: string
}

/**
 * Search knowledge base for semantically similar content
 */
export const searchSimilarContent = async (
  queryEmbedding: number[],
  options: SearchOptions = {}
): Promise<any[]> => {
  const {
    topK = 5,
    similarityThreshold = 0.3,
    domain,
    contentType,
  } = options

  try {
    // Build query filter
    const filter: Record<string, any> = {}
    if (domain) {
      filter.domain = domain
    }
    if (contentType) {
      filter['metadata.contentType'] = contentType
    }

    // Fetch all embeddings matching filters
    const embeddings = await KnowledgeEmbedding.find(filter)

    if (embeddings.length === 0) {
      return []
    }

    // Calculate similarity for each embedding
    const scoredResults = embeddings
      .map((embedding) => ({
        ...embedding.toObject(),
        similarity: cosineSimilarity(queryEmbedding, embedding.embedding),
      }))
      .filter((result) => result.similarity >= similarityThreshold)
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, topK)

    return scoredResults
  } catch (error) {
    console.error('Error searching similar content:', error)
    throw error
  }
}

/**
 * Convert search results to retrieved sources format for chat history
 */
export const formatRetrievedSources = (
  results: SearchResult[]
): IRetrievedSource[] => {
  return results.map((result) => ({
    title: result.title,
    content: result.content,
    domain: result.domain,
    similarity: result.similarity,
  }))
}

/**
 * Get retrieval stats for monitoring
 */
export const getRetrievalStats = async (): Promise<{
  totalEmbeddings: number
  domainBreakdown: Record<string, number>
  avgEmbeddingDimensions: number
}> => {
  try {
    const totalEmbeddings = await KnowledgeEmbedding.countDocuments()
    
    // Get domain breakdown
    const domainStats = await KnowledgeEmbedding.aggregate([
      {
        $group: {
          _id: '$domain',
          count: { $sum: 1 },
        },
      },
    ])

    const domainBreakdown = domainStats.reduce(
      (acc, stat) => {
        acc[stat._id || 'Unknown'] = stat.count
        return acc
      },
      {} as Record<string, number>
    )

    // Get avg embedding dimensions
    const sampleEmbedding = await KnowledgeEmbedding.findOne().select('embedding')
    const avgEmbeddingDimensions = sampleEmbedding?.embedding?.length || 768

    return {
      totalEmbeddings,
      domainBreakdown,
      avgEmbeddingDimensions,
    }
  } catch (error) {
    console.error('Error getting retrieval stats:', error)
    throw error
  }
}
