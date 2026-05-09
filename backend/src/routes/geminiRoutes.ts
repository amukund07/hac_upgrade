import { Router } from 'express'
import { handleGeminiRequest } from '../controllers/geminiController'

const router = Router()

router.post('/', handleGeminiRequest)

export default router
