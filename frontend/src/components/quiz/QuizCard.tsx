import { AnimatePresence, motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import { Badge } from '../ui/Badge'
import { OptionButton } from './OptionButton'

export interface QuizCardQuestion {
  id: string
  question: string
  options?: string[] | null
  correct_answer?: string
}

interface QuizCardProps {
  quizTitle: string
  question: QuizCardQuestion
  selectedAnswer: number | null
  isRevealed: boolean
  onAnswerSelect: (index: number) => void
}

export const QuizCard = ({ quizTitle, question, selectedAnswer, isRevealed, onAnswerSelect }: QuizCardProps) => {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={question.id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.35 }}
        className="w-full max-w-3xl mx-auto"
      >
        <div className="relative mb-6 overflow-hidden rounded-[1.5rem] border-2 border-terracotta-500/40 bg-gradient-to-br from-earth-900 via-earth-800 to-earth-900 p-6 md:p-8 md:mb-8 md:rounded-[2rem] shadow-[0_12px_40px_rgba(200,104,73,0.2)]">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(200,104,73,0.3),transparent_40%),radial-gradient(circle_at_bottom_right,rgba(200,104,73,0.2),transparent_35%)]" />
          <div className="relative">
            <Badge variant="category" className="mb-3 md:mb-4 gap-2 border-amber-400/50 bg-amber-500/20 text-amber-50">
              <Sparkles className="h-3 w-3" />
              {quizTitle}
            </Badge>
            <h2 className="font-serif text-2xl leading-tight text-white md:text-4xl font-bold">{question.question}</h2>
            <div className="mt-6 h-1 bg-gradient-to-r from-transparent via-terracotta-500/60 to-transparent" />
          </div>
        </div>

        <div className="space-y-3">
          {(question.options ?? []).map((answer, index) => {
            const isCorrect = answer === question.correct_answer
            const state = isRevealed
              ? isCorrect
                ? 'correct'
                : selectedAnswer === index
                  ? 'wrong'
                  : 'idle'
              : selectedAnswer === index
                ? 'selected'
                : 'idle'

            return (
              <OptionButton
                key={`${question.id}-${index}`}
                label={answer}
                state={state}
                disabled={isRevealed}
                onClick={() => onAnswerSelect(index)}
              />
            )
          })}
        </div>
      </motion.div>
    </AnimatePresence>
  )
}