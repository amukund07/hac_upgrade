/**
 * Knowledge Base Embedding Generation Script
 * Generates and stores embeddings for all knowledge base entries
 * Run this script to populate the KnowledgeEmbedding collection
 */

import { readFileSync } from 'fs'
import { resolve } from 'path'
import mongoose from 'mongoose'
import { KnowledgeEmbedding } from '../src/models/KnowledgeEmbedding'
import { generateEmbeddingsBatch } from '../src/ai/embeddings/embeddingService'
import { chunkKnowledgeEntry, getOptimalChunkSize } from '../src/ai/rag/chunking'
import { env } from '../src/config/env'

interface KnowledgeEntry {
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
  contentType?: 'remedy' | 'story' | 'technique' | 'historical' | 'practice' | 'general'
  [key: string]: any
}

/**
 * Load knowledge base from JSON file
 */
const loadKnowledgeBase = (): KnowledgeEntry[] => {
  try {
    const filePath = resolve(__dirname, '../data/knowledge_base/chatbot_rag_knowledge_base.json')
    const content = readFileSync(filePath, 'utf-8')
    const data = JSON.parse(content)
    console.log(`✓ Loaded ${Array.isArray(data) ? data.length : Object.keys(data).length} knowledge entries`)
    return Array.isArray(data) ? data : Object.values(data)
  } catch (error) {
    console.error('Error loading knowledge base:', error)
    throw error
  }
}

/**
 * Infer content type from domain/subdomain
 */
const inferContentType = (domain: string): KnowledgeEntry['contentType'] => {
  const typeMap: Record<string, KnowledgeEntry['contentType']> = {
    'home remedies': 'remedy',
    ayurveda: 'remedy',
    unani: 'remedy',
    'traditional martial arts': 'technique',
    yoga: 'technique',
    'sustainable farming': 'technique',
    'oral history': 'story',
    'traditional knowledge stories': 'story',
    'vedic mathematics': 'technique',
    'ancient astronomy': 'historical',
    'ancient texts': 'historical',
  }

  const lowerDomain = domain.toLowerCase()
  for (const [key, type] of Object.entries(typeMap)) {
    if (lowerDomain.includes(key)) {
      return type
    }
  }

  return 'general'
}

/**
 * Generate embeddings for a knowledge entry
 */
const generateEmbeddingsForEntry = async (
  entry: KnowledgeEntry,
  index: number,
  total: number
): Promise<void> => {
  try {
    // Determine optimal chunk size
    const contentType = entry.contentType || inferContentType(entry.domain)
    const chunkSize = getOptimalChunkSize(contentType)

    // Split entry into chunks
    const chunks = chunkKnowledgeEntry(entry, {
      chunkSize,
      overlapSize: Math.floor(chunkSize * 0.2), // 20% overlap
    })

    if (chunks.length === 0) {
      console.log(`⚠ Entry "${entry.title}" produced no chunks`)
      return
    }

    // Generate embeddings for all chunks
    const texts = chunks.map((chunk) => chunk.text)
    const embeddings = await generateEmbeddingsBatch(texts, 50) // 50ms delay between API calls

    // Store in database
    const embeddingDocuments = embeddings.map((embedding, chunkIdx) => ({
      title: entry.title,
      content: chunks[chunkIdx].text,
      chunkIndex: chunkIdx,
      domain: entry.domain,
      subdomain: entry.subdomain,
      embedding: embedding.embedding,
      metadata: {
        knowledgeId: entry.id,
        source: entry.domain,
        category: entry.subdomain || entry.domain,
        keywords: entry.keywords || [],
        contentType,
      },
    }))

    // Batch insert
    await KnowledgeEmbedding.insertMany(embeddingDocuments, { ordered: false })

    const progress = ((index + 1) / total) * 100
    console.log(
      `✓ [${progress.toFixed(1)}%] Processed "${entry.title}" (${chunks.length} chunks) - ${embeddingDocuments.length} embeddings stored`
    )
  } catch (error) {
    console.error(`✗ Error processing entry "${entry.title}":`, error instanceof Error ? error.message : error)
    // Continue processing other entries
  }
}

/**
 * Main execution
 */
const main = async () => {
  console.log('🚀 Starting knowledge base embedding generation...\n')

  try {
    // Connect to MongoDB
    console.log('📡 Connecting to MongoDB...')
    await mongoose.connect(env.mongoUri)
    console.log('✓ Connected to MongoDB\n')

    // Clear existing embeddings (optional, comment out to preserve)
    console.log('🗑 Clearing existing embeddings...')
    await KnowledgeEmbedding.deleteMany({})
    console.log('✓ Cleared existing embeddings\n')

    // Load knowledge base
    console.log('📚 Loading knowledge base...')
    const entries = loadKnowledgeBase()
    console.log(`✓ Found ${entries.length} entries\n`)

    if (entries.length === 0) {
      console.warn('⚠ No entries found in knowledge base')
      process.exit(0)
    }

    // Generate embeddings
    console.log('⚙ Generating embeddings (this may take a while)...\n')
    for (let i = 0; i < entries.length; i++) {
      await generateEmbeddingsForEntry(entries[i], i, entries.length)
      // Add delay between entries to avoid rate limiting
      if (i < entries.length - 1) {
        await new Promise((resolve) => setTimeout(resolve, 100))
      }
    }

    // Stats
    const totalEmbeddings = await KnowledgeEmbedding.countDocuments()
    const domainStats = await KnowledgeEmbedding.aggregate([
      {
        $group: {
          _id: '$domain',
          count: { $sum: 1 },
        },
      },
      { $sort: { count: -1 } },
    ])

    console.log('\n✅ Embedding generation complete!\n')
    console.log(`📊 Statistics:`)
    console.log(`   - Total embeddings: ${totalEmbeddings}`)
    console.log(`   - Total entries: ${entries.length}`)
    console.log(`   - Avg chunks per entry: ${(totalEmbeddings / entries.length).toFixed(1)}`)
    console.log(`\n📈 Domain breakdown:`)
    domainStats.forEach((stat) => {
      console.log(`   - ${stat._id}: ${stat.count} embeddings`)
    })

    process.exit(0)
  } catch (error) {
    console.error('❌ Fatal error:', error)
    process.exit(1)
  }
}

// Run if executed directly
if (require.main === module) {
  main()
}

export { generateEmbeddingsForEntry }
