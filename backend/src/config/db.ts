import mongoose from 'mongoose'
import { env } from './env'

export const connectDatabase = async () => {
  await mongoose.connect(env.mongoUri)
}

export const disconnectDatabase = async () => {
  await mongoose.disconnect()
}