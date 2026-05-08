import { motion } from 'framer-motion'
import { Check, X } from 'lucide-react'
import { cn } from '../../utils/utils'

interface AnswerCardProps {
  text: string
  isSelected: boolean
  isCorrect?: boolean
  isWrong?: boolean
  isRevealed: boolean
  onClick: () => void
  disabled?: boolean
}

export const AnswerCard = ({
  text,
  isSelected,
  isCorrect,
  isWrong,
  isRevealed,
  onClick,
  disabled,
}: AnswerCardProps) => {
  return (
    <motion.button
      whileHover={!disabled ? { scale: 1.01, y: -2 } : {}}
      whileTap={!disabled ? { scale: 0.99 } : {}}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'relative w-full rounded-2xl border-2 p-5 text-left transition-all duration-300',
        'backdrop-blur-sm disabled:cursor-not-allowed',
        !isRevealed && !isSelected && 'border-earth-200 bg-white/80 text-earth-800 hover:border-terracotta-300 hover:bg-terracotta-50/40 dark:border-earth-700 dark:bg-earth-900/50 dark:text-earth-100 dark:hover:border-terracotta-500/50',
        !isRevealed && isSelected && 'border-terracotta-500 bg-terracotta-50/80 text-earth-900 shadow-[0_0_24px_rgba(200,104,73,0.18)] dark:bg-terracotta-900/20 dark:text-earth-50',
        isRevealed && isCorrect && 'border-forest-500 bg-forest-50/80 text-forest-800 dark:bg-forest-900/20 dark:text-forest-200',
        isRevealed && isWrong && 'border-red-500 bg-red-50/80 text-red-800 dark:bg-red-900/20 dark:text-red-200',
      )}
    >
      <div className="flex items-center justify-between gap-4">
        <span className="flex-1 text-base font-medium leading-relaxed">{text}</span>

        {isRevealed && (
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: 'spring', stiffness: 220, damping: 16 }}
            className={cn(
              'flex h-7 w-7 items-center justify-center rounded-full',
              isCorrect && 'bg-forest-500 text-white',
              isWrong && 'bg-red-500 text-white',
            )}
          >
            {isCorrect ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
          </motion.div>
        )}
      </div>
    </motion.button>
  )
}