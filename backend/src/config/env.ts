import dotenv from 'dotenv'

dotenv.config()

const required = (value: string | undefined, fallback?: string) => {
  const resolved = value ?? fallback

  if (!resolved) {
    throw new Error('Missing required environment variable')
  }

  return resolved
}

export const env = {
  port: Number(process.env.PORT ?? 5000),
  mongoUri: required(process.env.MONGODB_URI, 'mongodb://127.0.0.1:27017/hackostic'),
  jwtSecret: required(process.env.JWT_SECRET, 'hackostic-development-secret'),
  jwtExpiresIn: process.env.JWT_EXPIRES_IN ?? '7d',
  clientOrigin: process.env.CLIENT_ORIGIN ?? 'http://localhost:5173',
  geminiApiKey: process.env.GEMINI_API_KEY ?? '',
}