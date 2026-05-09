import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate, useParams } from 'react-router-dom'
import { X } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { getQuizQuestions, submitQuizResult, type Quiz, type QuizQuestion } from '../../services/quizService'
import { apiClient } from '../../lib/apiClient'
import { QuizProgress } from '../../components/quiz/QuizProgress'
import { QuizCard } from '../../components/quiz/QuizCard'
import { QuizActionBar } from '../../components/quiz/QuizActionBar'
import { CelebrationModal } from '../../components/quiz/CelebrationModal'
import { FloatingParticles } from '../../components/quiz/FloatingParticles'
import { AICompanion } from '../../components/quiz/AICompanion'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'

type QuizPayload = Quiz & {
  earned_xp?: number
}

export const QuizPage = () => {
  const navigate = useNavigate();
  const { id } = useParams()
  const { user, refreshUser } = useAuth()
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null)
  const [isRevealed, setIsRevealed] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [quiz, setQuiz] = useState<QuizPayload | null>(null)
  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [earnedXp, setEarnedXp] = useState(0)
  const [answers, setAnswers] = useState<Record<number, number>>({})
  const [scorePercent, setScorePercent] = useState(0)

  useEffect(() => {
    const loadQuiz = async () => {
      if (!id) {
        setIsLoading(false)
        return
      }

      setIsLoading(true)
      const quizResponse = await apiClient.get<QuizPayload>(`/quizzes/${id}`)
      const questionResponse = await getQuizQuestions(id)

      setQuiz(quizResponse.data ?? null)
      setQuestions(questionResponse.data ?? [])
      setIsLoading(false)
    }

    void loadQuiz()
  }, [id])

  const question = questions[currentQuestion]
  const currentScore = useMemo(() => {
    if (!questions.length) {
      return 0
    }

    return questions.reduce((count, item, idx) => {
      const selectedIndex = answers[idx]
      const selectedText = typeof selectedIndex === 'number' ? item.options?.[selectedIndex] : undefined
      return count + (selectedText === item.correct_answer ? 1 : 0)
    }, 0)
  }, [answers, questions])

  const handleOptionClick = (idx: number) => {
    if (isRevealed) return
    setSelectedAnswer(idx)
  }

  const handleNext = () => {
    if (!isRevealed) {
      if (selectedAnswer === null) {
        return
      }

      setIsRevealed(true)
      setAnswers((currentAnswers) => ({ ...currentAnswers, [currentQuestion]: selectedAnswer }))
    } else {
      if (currentQuestion < questions.length - 1) {
        setCurrentQuestion((value) => value + 1)
        setSelectedAnswer(null)
        setIsRevealed(false)
      } else {
        void handleSubmitQuiz()
      }
    }
  }

  const handleSubmitQuiz = async () => {
    if (!quiz || !user || !questions.length) {
      return
    }

    const finalAnswers = { ...answers, [currentQuestion]: selectedAnswer ?? 0 }
    const finalScore = questions.reduce((count, item, idx) => {
      const selectedIndex = finalAnswers[idx]
      const selectedText = typeof selectedIndex === 'number' ? item.options?.[selectedIndex] : undefined
      return count + (selectedText === item.correct_answer ? 1 : 0)
    }, 0)

    const totalQuestions = questions.length
    const computedScorePercent = Math.round((finalScore / totalQuestions) * 100)
    const passed = quiz.passing_score ? computedScorePercent >= quiz.passing_score : finalScore === totalQuestions

    const submission = await submitQuizResult({
      user_id: user.id,
      quiz_id: quiz.id,
      score: finalScore,
      total_questions: totalQuestions,
      passed,
    })

    await refreshUser()
    setEarnedXp(submission.data?.earned_xp ?? 0)
    setScorePercent(computedScorePercent)
    setShowResults(true)
  }

  const handlePrevious = () => {
    if (currentQuestion === 0 || isLoading) {
      return
    }

    setCurrentQuestion((value) => Math.max(0, value - 1))
    const previousAnswer = answers[currentQuestion - 1] ?? null
    setSelectedAnswer(previousAnswer)
    setIsRevealed(Boolean(typeof previousAnswer === 'number'))
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-center p-4 bg-gradient-to-b from-earth-950 via-earth-900 to-earth-950">
        <div>
          <div className="mb-4 h-12 w-12 rounded-full border-4 border-terracotta-500/30 border-t-terracotta-500 animate-spin mx-auto" />
          <p className="text-lg font-semibold text-white">Loading quiz from the database...</p>
        </div>
      </div>
    )
  }

  if (showResults && quiz) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <CelebrationModal
          isOpen={showResults}
          isCorrect={scorePercent >= (quiz.passing_score ?? 70)}
          xpGained={earnedXp}
          onContinue={() => navigate(quiz.module_id ? `/modules/${quiz.module_id}` : '/modules')}
        />
        <motion.div initial={{ scale: 0.96, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="text-center max-w-md w-full">
          <Card className="p-8">
            <h2 className="font-serif text-3xl font-bold text-earth-900 dark:text-earth-50 mb-2">Quiz Complete!</h2>
            <p className="text-earth-600 dark:text-earth-400 mb-6">Your score has been saved and XP was added to your profile.</p>
            <div className="flex justify-center gap-4 mb-8">
              <div className="text-center">
                <p className="text-sm font-semibold text-earth-500">Score</p>
                <p className="text-2xl font-bold text-earth-900 dark:text-earth-100">{scorePercent}%</p>
              </div>
              <div className="w-px bg-earth-200 dark:bg-earth-800" />
              <div className="text-center">
                <p className="text-sm font-semibold text-earth-500">XP Earned</p>
                <p className="text-2xl font-bold text-terracotta-500">+{earnedXp}</p>
              </div>
            </div>
            <Button className="w-full" size="lg" onClick={() => navigate(quiz.module_id ? `/modules/${quiz.module_id}` : '/modules')}>
              Return to Module
            </Button>
          </Card>
        </motion.div>
      </div>
    )
  }

  if (!question) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-earth-950 via-earth-900 to-earth-950">
        <Card className="max-w-md w-full p-8 border-2 border-terracotta-500/40">
          <p className="text-center text-white text-lg font-semibold">Quiz questions are unavailable right now.</p>
          <Button className="w-full mt-6" onClick={() => navigate(-1)}>Return</Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-b from-earth-950 via-earth-900 to-earth-950 text-cream">
      <FloatingParticles />
      <div className="relative z-10 min-h-screen">
        <QuizProgress currentQuestion={currentQuestion + 1} totalQuestions={questions.length} />

        <div className="mx-auto flex min-h-screen max-w-4xl flex-col px-4 pb-36 pt-36 md:px-6">
          <div className="mb-8 flex items-center justify-between gap-4">
            <button onClick={() => navigate(-1)} className="inline-flex h-12 w-12 items-center justify-center rounded-full border-2 border-terracotta-500/50 bg-earth-800/80 text-white hover:border-terracotta-500 hover:text-white hover:bg-earth-700 transition-all">
              <X className="h-6 w-6" />
            </button>
            <div className="text-right">
              <p className="text-sm uppercase tracking-[0.28em] text-amber-300 font-semibold">Score</p>
              <p className="font-serif text-3xl text-white font-bold">{currentScore} / {questions.length}</p>
            </div>
          </div>

          <div className="flex-1">
            <QuizCard
              quizTitle={quiz?.title ?? 'Module quiz'}
              question={{
                id: question.id,
                question: question.question,
                options: question.options ?? [],
                correct_answer: question.correct_answer,
              }}
              selectedAnswer={selectedAnswer}
              isRevealed={isRevealed}
              onAnswerSelect={handleOptionClick}
            />
          </div>

          <div className="pointer-events-none fixed right-6 top-1/2 hidden -translate-y-1/2 lg:block">
            <AICompanion
              emotion={isRevealed ? 'encouraging' : 'thinking'}
              message={isRevealed ? 'Good. Review the feedback, then continue.' : 'Choose the answer that feels most aligned with the lesson.'}
            />
          </div>
        </div>

        <QuizActionBar
          currentQuestion={currentQuestion + 1}
          totalQuestions={questions.length}
          selectedAnswer={selectedAnswer}
          isRevealed={isRevealed}
          xpReward={25}
          onPrevious={handlePrevious}
          onNext={handleNext}
          onSubmit={handleSubmitQuiz}
          motivationalText={isRevealed ? 'That answer is locked in. Move to the next step.' : 'Trust the tradition and make your choice.'}
        />
      </div>
    </div>
  );
};
