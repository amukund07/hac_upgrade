import mongoose from 'mongoose'
import { env } from './env'

export const connectDatabase = async () => {
  try {
    await mongoose.connect(env.mongoUri)
    // eslint-disable-next-line no-console
    console.log('✓ MongoDB Connected')
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('✗ MongoDB Connection Error:', error)
    process.exit(1)
  }
}

export const disconnectDatabase = async () => {
  await mongoose.disconnect()
}