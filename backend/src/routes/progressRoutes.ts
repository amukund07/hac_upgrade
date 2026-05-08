import { Router } from 'express'
import { fetchUserLessonProgressController, fetchUserModuleProgress, recalculateProgress, updateUserModuleProgress } from '../controllers/progressController'
import { protect } from '../middleware/authMiddleware'

const router = Router()

router.get('/users/:userId/modules/:moduleId/progress', fetchUserModuleProgress)
router.put('/users/:userId/modules/:moduleId/progress', protect, updateUserModuleProgress)
router.get('/users/:userId/lessons/:lessonId/progress', fetchUserLessonProgressController)
router.post('/users/:userId/modules/:moduleId/recalculate', protect, recalculateProgress)

export default router