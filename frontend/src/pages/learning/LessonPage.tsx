import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate, useParams } from 'react-router-dom'
import { X, Check, Award, Volume2, VolumeX } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { ProgressBar } from '../../components/ui/ProgressBar'
import { useAuth } from '../../context/AuthContext'
import { completeLesson, getLessonById, type Lesson } from '../../services/lessonService'
import { getQuizByModule, type Quiz } from '../../services/quizService'
import { useLessonNarration } from '../../hooks/useLessonNarration'

export const LessonPage = () => {
  const navigate = useNavigate();
  const { id } = useParams()
  const { user, refreshUser } = useAuth()
  const { playNarration, stopNarration, isSpeaking, isGenerating, error } = useLessonNarration()
  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showReward, setShowReward] = useState(false)
  const [isCompleting, setIsCompleting] = useState(false)
  const didNarrate = useRef(false)

  useEffect(() => {
    const loadLesson = async () => {
      if (!id) {
        setIsLoading(false)
        return
      }

      setIsLoading(true)
      const lessonResult = await getLessonById(id)
      setLesson(lessonResult.data)

      if (lessonResult.data) {
        const quizResult = await getQuizByModule(lessonResult.data.module_id)
        setQuiz(quizResult.data)
      }

      setIsLoading(false)
    }

    void loadLesson()
  }, [id])

  useEffect(() => {
    if (!lesson || didNarrate.current) {
      return
    }

    didNarrate.current = true
    void playNarration(lesson.module_id, lesson.title, lesson.content)
  }, [lesson, playNarration])

  const handleComplete = async () => {
    if (!lesson || !quiz || !user) {
      return
    }

    setIsCompleting(true)
    try {
      await completeLesson(user.id, lesson.id)
      await refreshUser()
      setShowReward(true)
      setTimeout(() => {
        navigate(`/quiz/${quiz.id}?lessonId=${lesson.id}`)
      }, 1600)
    } finally {
      setIsCompleting(false)
    }
  };

  const handleNarrationToggle = async () => {
    if (!lesson) {
      return
    }

    if (isSpeaking) {
      stopNarration()
      return
    }

    await playNarration(lesson.module_id, lesson.title, lesson.content)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-earth-500 dark:text-earth-300">
        Loading lesson from the database...
      </div>
    )
  }

  if (!lesson) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <Card className="max-w-md text-center space-y-4">
          <h1 className="font-serif text-3xl font-bold text-earth-900 dark:text-earth-50">Lesson not found</h1>
          <p className="text-earth-600 dark:text-earth-400">The requested lesson could not be loaded.</p>
          <Button onClick={() => navigate('/modules')}>Back to modules</Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-paper-light dark:bg-paper-dark">
      {/* Navbar for Lesson */}
      <div className="sticky top-0 z-40 bg-white/80 dark:bg-earth-900/80 backdrop-blur-md border-b border-earth-200 dark:border-earth-800 px-4 py-3 flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="p-2 text-earth-500 hover:bg-earth-100 rounded-full dark:hover:bg-earth-800">
          <X className="h-6 w-6" />
        </button>
        <div className="flex-1 max-w-xl mx-4">
          <ProgressBar progress={showReward ? 100 : 60} variant="success" />
        </div>
        <div className="text-sm font-bold text-forest-600 dark:text-forest-400">
          Lesson
        </div>
      </div>

      {/* Content */}
      <div className="max-w-3xl mx-auto px-6 py-12 pb-32">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-8"
        >
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.3em] text-forest-600 dark:text-forest-400 mb-2">Live lesson</p>
              <h1 className="font-serif text-4xl font-bold text-earth-900 dark:text-earth-50">{lesson.title}</h1>
            </div>
            <Button variant="outline" size="sm" onClick={handleNarrationToggle} isLoading={isGenerating}>
              {isSpeaking ? <VolumeX className="mr-2 h-4 w-4" /> : <Volume2 className="mr-2 h-4 w-4" />}
              {isSpeaking ? 'Stop voice' : 'Play voice'}
            </Button>
          </div>
          


          <div className="prose prose-lg dark:prose-invert prose-earth max-w-none font-sans text-earth-700 dark:text-earth-300">
            <p>
              {lesson.content}
            </p>
            
            <Card className="my-8 bg-forest-50/50 dark:bg-forest-900/20 border-forest-200 dark:border-forest-800">
              <h3 className="font-serif text-xl font-bold text-forest-800 dark:text-forest-200 mb-4">Study tip</h3>
              <ol className="space-y-4 list-decimal list-inside">
                <li>Read the narration once, then listen to the voice version.</li>
                <li>Complete the lesson to unlock the quiz.</li>
                <li>Your quiz score determines the XP added to your profile.</li>
              </ol>
            </Card>

            <p>
              {quiz ? `After this lesson, you will take the ${quiz.title} quiz to earn XP.` : 'The related quiz is being loaded from the database.'}
            </p>
            {error && <p className="text-terracotta-600 dark:text-terracotta-400">{error}</p>}
          </div>
        </motion.div>
      </div>

      {/* Bottom Bar */}
      <div className="fixed bottom-0 w-full bg-white dark:bg-earth-900 border-t border-earth-200 dark:border-earth-800 p-4 z-40">
        <div className="max-w-3xl mx-auto flex justify-end">
          <Button size="lg" onClick={handleComplete} isLoading={isCompleting}>
            <Check className="mr-2 h-5 w-5" /> Mark Complete & Continue
          </Button>
        </div>
      </div>

      {/* Reward Overlay */}
      <AnimatePresence>
        {showReward && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.8, y: 50 }}
              animate={{ scale: 1, y: 0 }}
              className="bg-white dark:bg-earth-900 p-8 rounded-3xl text-center max-w-sm mx-4 shadow-2xl"
            >
              <div className="mx-auto w-24 h-24 bg-yellow-100 dark:bg-yellow-900/50 rounded-full flex items-center justify-center mb-6 shadow-inner">
                <Award className="h-12 w-12 text-yellow-500" />
              </div>
              <h2 className="font-serif text-3xl font-bold text-earth-900 dark:text-earth-50 mb-2">Lesson Complete!</h2>
              <p className="text-earth-600 dark:text-earth-400 mb-6">The quiz is unlocked. Your XP will be awarded after scoring the quiz.</p>
              <div className="inline-flex items-center justify-center px-4 py-2 bg-terracotta-100 dark:bg-terracotta-900/50 text-terracotta-600 dark:text-terracotta-400 rounded-full font-bold text-xl">
                Quiz unlocked
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
