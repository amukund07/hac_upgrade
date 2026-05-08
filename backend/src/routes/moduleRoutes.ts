import { Router } from 'express'
import { fetchModule, listModules, moduleLessons, moduleQuizzes, moduleQuiz } from '../controllers/moduleController'

const router = Router()

router.get('/', listModules)
router.get('/:id', fetchModule)
router.get('/:moduleId/lessons', moduleLessons)
router.get('/:moduleId/quizzes', moduleQuizzes)
router.get('/:moduleId/quiz', moduleQuiz)

export default router