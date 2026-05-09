/**
 * RAG Pipeline Type Definitions
 * Shared types for embedding, retrieval, and chat services
 */

/**
 * Search result from vector database
 */
export interface RAGSearchResult {
  id: string
  title: string
  content: string
  domain: string
  subdomain?: string
  similarity: number
  chunkIndex: number
  embedding: number[]
  metadata: {
    knowledgeId?: string
    source?: string
    category?: string
    keywords?: string[]
    contentType?: 'remedy' | 'story' | 'technique' | 'historical' | 'practice' | 'general'
  }
}

/**
 * Chat message with optional sources
 */
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'elder'
  text: string
  sources?: ChatSource[]
  timestamp?: Date
  sessionId?: string
}

/**
 * Reference to knowledge source
 */
export interface ChatSource {
  title: string
  domain: string
  subdomain?: string
  similarity: number
  chunkIndex?: number
}

/**
 * RAG query configuration
 */
export interface RAGQueryOptions {
  userId?: string
  sessionId?: string
  domain?: string
  contentType?: 'remedy' | 'story' | 'technique' | 'historical' | 'practice' | 'general'
  topK?: number
  similarityThreshold?: number
  includeSources?: boolean
}

/**
 * RAG response
 */
export interface RAGResponse {
  response: string
  sources: ChatSource[]
  sessionId: string
  responseTime: number
  model?: string
  confidence?: number
}

/**
 * Chat history entry
 */
export interface ChatHistoryEntry {
  _id?: string
  userId?: string
  sessionId: string
  query: string
  response: string
  retrievedSources: ChatSource[]
  modelUsed: string
  responseTime: number
  createdAt: Date
  updatedAt: Date
}

/**
 * Embedding result
 */
export interface EmbeddingResult {
  text: string
  embedding: number[]
  dimensions: number
}

/**
 * Batch embedding result
 */
export interface BatchEmbeddingResult {
  successful: number
  failed: number
  results: EmbeddingResult[]
  errors: Array<{ text: string; error: string }>
}

/**
 * Knowledge entry for embedding
 */
export interface KnowledgeEntry {
  id?: string
  title: string
  domain: string
  subdomain?: string
  content?: string
  dadi_story?: string
  summary?: string
  health_benefits?: string[]
  remedy_steps?: string[]
  ingredients?: string[]
  scientific_backing?: string[]
  modern_relevance?: string[]
  keywords?: string[]
  yoga_poses?: string[]
  contraindications?: string[]
  pubmed_abstracts?: string[]
  contentType?: 'remedy' | 'story' | 'technique' | 'historical' | 'practice' | 'general'
  [key: string]: any
}

/**
 * Chunked content
 */
export interface ContentChunk {
  text: string
  chunkIndex: number
  startIndex: number
  endIndex: number
}

/**
 * Vector search options
 */
export interface VectorSearchOptions {
  topK?: number
  similarityThreshold?: number
  domain?: string
  contentType?: string
  maxDomains?: number
}

/**
 * Retrieval statistics
 */
export interface RetrievalStats {
  totalEmbeddings: number
  domainBreakdown: Record<string, number>
  avgEmbeddingDimensions: number
  generatedAt: Date
}

/**
 * Chat session
 */
export interface ChatSession {
  sessionId: string
  userId?: string
  createdAt: Date
  lastActivityAt: Date
  messageCount: number
  domains: string[]
  status: 'active' | 'archived' | 'deleted'
}

/**
 * Embedding generation progress
 */
export interface EmbeddingProgress {
  currentEntry: number
  totalEntries: number
  currentChunk: number
  totalChunks: number
  successCount: number
  failureCount: number
  percentComplete: number
  elapsedTime: number
  estimatedTimeRemaining: number
}

/**
 * Error types
 */
export type RAGError = 
  | 'EMBEDDING_FAILED'
  | 'SEARCH_FAILED'
  | 'GENERATION_FAILED'
  | 'STORAGE_FAILED'
  | 'INVALID_INPUT'
  | 'NO_CONTEXT_FOUND'
  | 'API_ERROR'
  | 'DB_ERROR'
  | 'UNKNOWN'

/**
 * Error response
 */
export interface RAGErrorResponse {
  error: RAGError
  message: string
  details?: Record<string, any>
  statusCode: number
  timestamp: Date
}

/**
 * Configuration for RAG system
 */
export interface RAGConfig {
  enableCaching?: boolean
  enableLogging?: boolean
  similarityThreshold?: number
  defaultTopK?: number
  chunkSize?: number
  chunkOverlap?: number
  embeddingModel?: string
  generationModel?: string
  timeoutMs?: number
}
