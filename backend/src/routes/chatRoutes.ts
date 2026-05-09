import { Router } from 'express'
import { chat, getChatHistoryHandler } from '../controllers/chatController'

const router = Router()

// POST /api/chat/query - Send a chat query and get RAG response
router.post('/query', chat)

// GET /api/chat/history/:sessionId - Get chat history for a session
router.get('/history/:sessionId', getChatHistoryHandler)

export default router
