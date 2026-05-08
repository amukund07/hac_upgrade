import { Router } from 'express'
import { fetchLeaderboard } from '../controllers/leaderboardController'

const router = Router()

router.get('/', fetchLeaderboard)

export default router