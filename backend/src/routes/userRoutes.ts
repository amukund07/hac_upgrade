import { Router } from 'express'
import { fetchUserProfile, patchUserProfile, updateUserXp } from '../controllers/userController'
import { protect } from '../middleware/authMiddleware'

const router = Router()

router.get('/:userId', fetchUserProfile)
router.put('/:userId/xp', protect, updateUserXp)
router.put('/me', protect, patchUserProfile)

export default router