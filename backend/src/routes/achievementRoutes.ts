import { Router } from 'express'
import { fetchAchievements, fetchUserAchievements, unlockAchievementController } from '../controllers/achievementController'
import { protect } from '../middleware/authMiddleware'

const router = Router()

router.get('/', fetchAchievements)
router.get('/users/:userId', fetchUserAchievements)
router.post('/unlock', protect, unlockAchievementController)

export default router