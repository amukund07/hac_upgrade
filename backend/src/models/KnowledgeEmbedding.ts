import { Schema, model, Document } from 'mongoose'

export interface IKnowledgeEmbedding extends Document {
  title: string
  content: string
  chunkIndex: number
  domain: string
  subdomain?: string
  embedding: number[]
  metadata: {
    knowledgeId?: string
    source?: string
    category?: string
    keywords?: string[]
    contentType?: 'remedy' | 'story' | 'technique' | 'historical' | 'practice' | 'general'
  }
  createdAt: Date
  updatedAt: Date
}

const KnowledgeEmbeddingSchema = new Schema<IKnowledgeEmbedding>(
  {
    title: {
      type: String,
      required: true,
      index: true,
    },
    content: {
      type: String,
      required: true,
    },
    chunkIndex: {
      type: Number,
      required: true,
      default: 0,
    },
    domain: {
      type: String,
      required: true,
      index: true,
    },
    subdomain: {
      type: String,
      index: true,
    },
    embedding: {
      type: [Number],
      required: true,
    },
    metadata: {
      knowledgeId: String,
      source: String,
      category: String,
      keywords: [String],
      contentType: {
        type: String,
        enum: ['remedy', 'story', 'technique', 'historical', 'practice', 'general'],
        default: 'general',
      },
    },
  },
  { timestamps: true }
)

// Create index for vector search (basic similarity)
KnowledgeEmbeddingSchema.index({ 'metadata.category': 1, 'metadata.contentType': 1 })

export const KnowledgeEmbedding = model<IKnowledgeEmbedding>(
  'KnowledgeEmbedding',
  KnowledgeEmbeddingSchema
)
