interface QuizProgressProps {
  currentQuestion: number
  totalQuestions: number
}

export const QuizProgress = ({ currentQuestion, totalQuestions }: QuizProgressProps) => {
  const progress = totalQuestions > 0 ? (currentQuestion / totalQuestions) * 100 : 0

  return (
    <div className="fixed top-[73px] left-0 right-0 z-30 border-b border-terracotta-500/10 bg-earth-950/80 px-6 py-3 backdrop-blur-sm">
      <div className="mx-auto max-w-3xl">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-sm text-earth-300">Question {currentQuestion} / {totalQuestions}</span>
          <span className="text-sm text-terracotta-300">{Math.round(progress)}% Complete</span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-earth-700/60">
          <div className="h-full rounded-full bg-gradient-to-r from-terracotta-500 to-burnt-orange-500 transition-all duration-500" style={{ width: `${progress}%` }} />
        </div>
      </div>
    </div>
  )
}