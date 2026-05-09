import { Schema, model, Document } from 'mongoose'

export interface IRetrievedSource {
  title: string
  content: string
  domain: string
  similarity: number
}

export interface IChatHistory extends Document {
  userId?: string
  sessionId: string
  query: string
  response: string
  retrievedSources: IRetrievedSource[]
  modelUsed: string
  responseTime: number
  createdAt: Date
  updatedAt: Date
}

const RetrievedSourceSchema = new Schema(
  {
    title: {
      type: String,
      required: true,
    },
    content: {
      type: String,
      required: true,
    },
    domain: {
      type: String,
      required: true,
    },
    similarity: {
      type: Number,
      required: true,
    },
  },
  { _id: false }
)

const ChatHistorySchema = new Schema<IChatHistory>(
  {
    userId: {
      type: String,
      index: true,
    },
    sessionId: {
      type: String,
      required: true,
      index: true,
    },
    query: {
      type: String,
      required: true,
    },
    response: {
      type: String,
      required: true,
    },
    retrievedSources: [RetrievedSourceSchema],
    modelUsed: {
      type: String,
      default: 'gemini-2.0-flash',
    },
    responseTime: {
      type: Number,
      required: true,
    },
  },
  { timestamps: true }
)

ChatHistorySchema.index({ sessionId: 1, createdAt: -1 })
ChatHistorySchema.index({ userId: 1, createdAt: -1 })

export const ChatHistory = model<IChatHistory>('ChatHistory', ChatHistorySchema)
