import { Router } from 'express'
import { currentUser, login, logout, register, updateMe } from '../controllers/authController'
import { protect } from '../middleware/authMiddleware'

const router = Router()

router.post('/register', register)
router.post('/login', login)
router.post('/logout', protect, logout)
router.get('/me', protect, currentUser)
router.put('/me', protect, updateMe)

export default router