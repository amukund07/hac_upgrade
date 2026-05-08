import { ChevronLeft, ChevronRight, CheckCircle, Zap } from 'lucide-react'
import { Button } from '../ui/Button'
import { motion, AnimatePresence } from 'framer-motion'

interface QuizActionBarProps {
  currentQuestion: number
  totalQuestions: number
  selectedAnswer: number | null
  isRevealed: boolean
  xpReward: number
  onPrevious: () => void
  onNext: () => void
  onSubmit: () => void
  motivationalText: string
}

export const QuizActionBar = ({
  currentQuestion,
  totalQuestions,
  selectedAnswer,
  isRevealed,
  xpReward,
  onPrevious,
  onNext,
  onSubmit,
  motivationalText,
}: QuizActionBarProps) => {
  const isFirstQuestion = currentQuestion === 1
  const isLastQuestion = currentQuestion === totalQuestions

  return (
    <motion.div
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      className="fixed bottom-0 left-0 right-0 z-40 border-t border-terracotta-500/15 bg-earth-950/95 backdrop-blur-md"
    >
      <div className="mx-auto max-w-3xl px-6 py-5">
        <div className="flex items-center justify-between gap-4">
          <Button variant="outline" onClick={onPrevious} disabled={isFirstQuestion} className="border-terracotta-400/30 text-cream hover:bg-terracotta-500/10 hover:text-cream">
            <ChevronLeft className="mr-1 h-4 w-4" />
            Previous
          </Button>

          <div className="flex flex-1 flex-col items-center gap-1 text-center">
            <AnimatePresence mode="wait">
              <motion.p
                key={motivationalText}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="text-sm text-earth-300"
              >
                {motivationalText}
              </motion.p>
            </AnimatePresence>

            {selectedAnswer !== null && (
              <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="flex items-center gap-1.5 text-antique-gold-300">
                <Zap className="h-4 w-4 fill-current" />
                <span className="text-sm font-medium">+{xpReward} XP</span>
              </motion.div>
            )}
          </div>

          {!isLastQuestion ? (
            <Button onClick={onNext} disabled={!isRevealed} className="bg-gradient-to-r from-terracotta-500 to-burnt-orange-500 text-white disabled:opacity-50">
              Next Question
              <ChevronRight className="ml-1 h-4 w-4" />
            </Button>
          ) : (
            <Button onClick={onSubmit} disabled={!isRevealed} className="bg-gradient-to-r from-forest-600 to-forest-500 text-white disabled:opacity-50">
              <CheckCircle className="mr-1.5 h-4 w-4" />
              Submit Quiz
            </Button>
          )}
        </div>
      </div>
    </motion.div>
  )
}