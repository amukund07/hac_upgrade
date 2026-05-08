import { Router } from 'express'
import { fetchQuizQuestions, fetchQuizByModule, submitQuiz } from '../controllers/quizController'
import { protect } from '../middleware/authMiddleware'

const router = Router()

router.get('/:quizId', fetchQuizByModule)
router.get('/:quizId/questions', fetchQuizQuestions)
router.post('/:quizId/submit', protect, submitQuiz)

export default router