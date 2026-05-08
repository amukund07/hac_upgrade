import { Router } from 'express'
import { completeLessonController, fetchLesson, fetchUserLessonProgress } from '../controllers/lessonController'
import { protect } from '../middleware/authMiddleware'

const router = Router()

router.get('/users/:userId/:lessonId/progress', fetchUserLessonProgress)
router.get('/:id', fetchLesson)
router.post('/:id/complete', protect, completeLessonController)

export default router