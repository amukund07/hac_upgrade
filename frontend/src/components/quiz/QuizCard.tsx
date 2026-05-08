import { AnimatePresence, motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import { Badge } from '../ui/Badge'
import { AnswerCard } from './AnswerCard'

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
        <div className="relative mb-6 overflow-hidden rounded-3xl border border-terracotta-200/40 bg-gradient-to-br from-earth-950 to-earth-900 p-8 shadow-[0_12px_40px_rgba(0,0,0,0.25)] dark:border-terracotta-500/20">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(200,104,73,0.22),transparent_35%),radial-gradient(circle_at_bottom_right,rgba(74,103,65,0.16),transparent_30%)]" />
          <div className="relative">
            <Badge variant="category" className="mb-4 gap-2 border-terracotta-500/30 bg-terracotta-500/15 text-cream">
              <Sparkles className="h-3 w-3" />
              {quizTitle}
            </Badge>
            <h2 className="font-serif text-3xl leading-tight text-cream md:text-4xl">{question.question}</h2>
            <div className="mt-6 h-px bg-gradient-to-r from-transparent via-terracotta-400/40 to-transparent" />
          </div>
        </div>

        <div className="space-y-3">
          {(question.options ?? []).map((answer, index) => {
            const isCorrect = answer === question.correct_answer

            return (
              <AnswerCard
                key={`${question.id}-${index}`}
                text={answer}
                isSelected={selectedAnswer === index}
                isCorrect={isRevealed && isCorrect}
                isWrong={isRevealed && selectedAnswer === index && !isCorrect}
                isRevealed={isRevealed}
                onClick={() => onAnswerSelect(index)}
                disabled={isRevealed}
              />
            )
          })}
        </div>
      </motion.div>
    </AnimatePresence>
  )
}