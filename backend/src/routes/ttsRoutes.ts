import { Router } from 'express'
import { synthesize } from '../controllers/ttsController'

const router = Router()

router.post('/', synthesize)

export default router
