import { AnimatePresence, motion } from 'framer-motion'
import { ChevronLeft, ChevronRight, CheckCircle, Sparkles } from 'lucide-react'
import { Button } from '../ui/Button'
import { XPAnimation } from './XPAnimation'

interface QuizActionBarProps {
  currentQuestion: number
  totalQuestions: number
  selectedAnswer: number | null
  isRevealed: boolean
  isSubmitting?: boolean
  xpReward: number
  onPrevious: () => void
  onNext: () => void
  onSubmit: () => Promise<void>
  motivationalText: string
}

export const QuizActionBar = ({
  currentQuestion,
  totalQuestions,
  selectedAnswer,
  isRevealed,
  isSubmitting = false,
  xpReward,
  onPrevious,
  onNext,
  onSubmit,
  motivationalText,
}: QuizActionBarProps) => {
  const isFirstQuestion = currentQuestion === 1
  const isLastQuestion = currentQuestion === totalQuestions

  const handlePrimaryAction = () => {
    if (isRevealed && isLastQuestion) {
      void onSubmit()
    } else {
      onNext()
    }
  }

  const primaryLabel = !isRevealed 
    ? 'Reveal Answer' 
    : isLastQuestion 
      ? 'Complete Quiz' 
      : 'Next Question'

  return (
    <motion.div
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      className="fixed bottom-0 left-0 right-0 z-40 border-t-2 border-terracotta-500/30 bg-earth-950/98 backdrop-blur-xl"
    >
      <div className="mx-auto max-w-5xl px-4 py-5 md:px-6">
        <div className="flex items-center justify-between gap-4 rounded-2xl border-2 border-terracotta-500/40 bg-gradient-to-r from-earth-900 to-earth-800 px-6 py-5 backdrop-blur-xl shadow-lg shadow-terracotta-500/10">
          <Button 
            variant="outline" 
            onClick={onPrevious} 
            disabled={isFirstQuestion || isSubmitting} 
            className="rounded-full border-2 border-white/40 text-white hover:bg-white/15 hover:text-white font-semibold"
          >
            <ChevronLeft className="mr-2 h-5 w-5" />
            Previous
          </Button>

          <div className="flex flex-1 flex-col items-center gap-1 text-center">
            <AnimatePresence mode="wait">
              <motion.p
                key={motivationalText}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="text-base font-medium text-white"
              >
                {motivationalText}
              </motion.p>
            </AnimatePresence>

            {selectedAnswer !== null && (
              <XPAnimation xp={xpReward} />
            )}
          </div>

          <Button
            onClick={handlePrimaryAction}
            disabled={isSubmitting || (!isRevealed && selectedAnswer === null)}
            className="rounded-full bg-gradient-to-r from-terracotta-500 via-burnt-orange-500 to-burnt-orange-600 text-white shadow-lg shadow-terracotta-500/30 hover:shadow-terracotta-500/50 disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-base"
          >
            {!isRevealed ? <Sparkles className="mr-2 h-5 w-5" /> : <CheckCircle className="mr-2 h-5 w-5" />}
            {primaryLabel}
            <ChevronRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      </div>
    </motion.div>
  )
}