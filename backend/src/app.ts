import express from 'express'
import cors from 'cors'
import { env } from './config/env'
import authRoutes from './routes/authRoutes'
import moduleRoutes from './routes/moduleRoutes'
import lessonRoutes from './routes/lessonRoutes'
import quizRoutes from './routes/quizRoutes'
import progressRoutes from './routes/progressRoutes'
import leaderboardRoutes from './routes/leaderboardRoutes'
import achievementRoutes from './routes/achievementRoutes'
import userRoutes from './routes/userRoutes'
import ttsRoutes from './routes/ttsRoutes'
import chatRoutes from './routes/chatRoutes'
import geminiRoutes from './routes/geminiRoutes'
import { errorHandler, notFound } from './middleware/errorMiddleware'

export const app = express()

app.use(
  cors({
    origin: env.clientOrigin,
    credentials: true,
  }),
)
app.use(express.json())

app.get('/health', (_req, res) => {
  res.json({ success: true, message: 'Hackostic API is running' })
})

app.use('/api/auth', authRoutes)
app.use('/api/modules', moduleRoutes)
app.use('/api/lessons', lessonRoutes)
app.use('/api/quizzes', quizRoutes)
app.use('/api/progress', progressRoutes)
app.use('/api/leaderboard', leaderboardRoutes)
app.use('/api/achievements', achievementRoutes)
app.use('/api/users', userRoutes)
app.use('/api/tts', ttsRoutes)
app.use('/api/chat', chatRoutes)
app.use('/api/gemini', geminiRoutes)

app.use(notFound)
app.use(errorHandler)