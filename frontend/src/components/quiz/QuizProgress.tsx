interface QuizProgressProps {
  currentQuestion: number
  totalQuestions: number
}

export const QuizProgress = ({ currentQuestion, totalQuestions }: QuizProgressProps) => {
  const progress = totalQuestions > 0 ? (currentQuestion / totalQuestions) * 100 : 0

  return (
    <div className="fixed top-[73px] left-0 right-0 z-30 border-b border-white/10 bg-earth-950/70 px-4 py-3 backdrop-blur-xl md:px-6">
      <div className="mx-auto max-w-5xl">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-xs uppercase tracking-[0.28em] text-earth-300">Question {currentQuestion} / {totalQuestions}</span>
          <span className="text-xs uppercase tracking-[0.28em] text-amber-300">{Math.round(progress)}% complete</span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-earth-700/60">
          <div className="h-full rounded-full bg-gradient-to-r from-amber-300 via-orange-400 to-terracotta-500 transition-all duration-500" style={{ width: `${progress}%` }} />
        </div>
      </div>
    </div>
  )
}