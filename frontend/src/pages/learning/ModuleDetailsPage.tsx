import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate, useParams } from 'react-router-dom'
import { ChevronLeft, Play, Lock, CheckCircle2, Files, Sparkles } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { useAuth } from '../../context/AuthContext'
import { getModuleById, getModuleLessons, getModuleQuizzes, type LearningModule, type Lesson, type Quiz } from '../../services/moduleService'
import { getUserLessonProgress } from '../../services/lessonService'

export const ModuleDetailsPage = () => {
  const navigate = useNavigate();
  const { id } = useParams()
  const { user } = useAuth()
  const [module, setModule] = useState<LearningModule | null>(null)
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [quizzes, setQuizzes] = useState<Quiz[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [lessonProgressMap, setLessonProgressMap] = useState<Record<string, boolean>>({})

  useEffect(() => {
    const loadModule = async () => {
      if (!id) {
        setIsLoading(false)
        return
      }

      setIsLoading(true)
      const moduleResult = await getModuleById(id)
      const lessonsResult = await getModuleLessons(id)
      const quizzesResult = await getModuleQuizzes(id)

      setModule(moduleResult.data)
      setLessons(lessonsResult.data ?? [])
      setQuizzes(quizzesResult.data ?? [])
      setIsLoading(false)
    }

    void loadModule()
  }, [id])

  const lessonStatuses = useMemo(() => {
    if (!lessons.length) {
      return []
    }

    const completedCount = lessons.reduce((count, lesson) => count + (lessonProgressMap[lesson.id] ? 1 : 0), 0)

    return lessons.map((lesson, index) => {
      const completed = Boolean(lessonProgressMap[lesson.id])
      const status = completed
        ? 'completed'
        : index === completedCount
          ? 'unlocked'
          : 'locked'

      return { lesson, status }
    })
  }, [lessonProgressMap, lessons])

  useEffect(() => {
    const hydrateLessonProgress = async () => {
      if (!user || !lessons.length) {
        return
      }

      const progressEntries = await Promise.all(
        lessons.map(async (lesson) => {
          const progressResult = await getUserLessonProgress(user.id, lesson.id)
          return {
            lessonId: lesson.id,
            completed: Boolean(progressResult.data?.completed),
          }
        }),
      )

      setLessonProgressMap(
        progressEntries.reduce<Record<string, boolean>>((accumulator, entry) => {
          accumulator[entry.lessonId] = entry.completed
          return accumulator
        }, {}),
      )
    }

    void hydrateLessonProgress()
  }, [lessons, user?.id])

  const completedLessonsCount = lessons.filter((lesson) => lessonProgressMap[lesson.id]).length
  const progressPercent = lessons.length ? Math.round((completedLessonsCount / lessons.length) * 100) : 0

  const startQuiz = (quizId: string) => {
    if (!quizId) {
      return
    }

    navigate(`/quiz/${quizId}`)
  }

  return (
    <div className="pb-24">
      {/* Hero Banner */}
      <div className="relative h-64 md:h-80 w-full bg-forest-900 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-earth-900/90 to-transparent z-10" />

        <div className="absolute top-4 left-4 z-20">
          <button 
            onClick={() => navigate('/modules')}
            className="flex items-center justify-center h-10 w-10 rounded-full bg-white/20 text-white backdrop-blur-md hover:bg-white/30 transition-colors"
          >
            <ChevronLeft className="h-6 w-6" />
          </button>
        </div>
        <div className="absolute bottom-0 left-0 w-full p-6 md:p-8 z-20">
          <div className="max-w-4xl mx-auto flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <Badge variant="category" className="bg-forest-500/30 text-white border-forest-400/50 mb-3 backdrop-blur-sm">{module?.category ?? 'Learning Module'}</Badge>
              <h1 className="font-serif text-3xl md:text-5xl font-bold text-white mb-2">{module?.title ?? 'Loading module...'}</h1>
              <p className="text-earth-200 text-lg max-w-xl">{module?.description ?? 'Fetching lessons and quiz from the database.'}</p>
            </div>
            <div className="flex items-center gap-4 bg-black/30 backdrop-blur-md p-4 rounded-xl border border-white/10 shrink-0">
              <div className="text-center">
                <p className="text-xs text-earth-300 uppercase font-semibold">Progress</p>
                <p className="text-xl font-bold text-white">{progressPercent}%</p>
              </div>
              <div className="h-10 w-px bg-white/20 mx-2" />
              <div className="text-center">
                <p className="text-xs text-earth-300 uppercase font-semibold">Reward</p>
                <p className="text-xl font-bold text-terracotta-400">+{module?.xp_reward ?? 0} XP</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-6 md:p-8 mt-4">
        {/* Cultural Quote */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card className="bg-earth-100/50 dark:bg-earth-900/30 border-l-4 border-l-terracotta-500 rounded-l-none">
            <p className="font-serif text-lg italic text-earth-800 dark:text-earth-200">
              "{module?.hero_story ?? 'The lesson path is being assembled from live database content.'}"
            </p>
            <p className="text-sm font-semibold text-earth-500 mt-2">— Traditional Indian Proverb</p>
          </Card>
        </motion.div>

        {/* Journey/Timeline */}
        <div className="mt-12">
          <h2 className="font-serif text-2xl font-bold text-earth-900 dark:text-earth-50 mb-8">Your Journey</h2>

          {isLoading && (
            <Card className="text-earth-600 dark:text-earth-400">Loading lessons from the database...</Card>
          )}
          
          <div className="space-y-6">
              {lessonStatuses.map(({ lesson, status }, idx) => (
              <motion.div
                  key={lesson.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="relative pl-10"
              >
                {/* Connecting Line */}
                {idx !== lessons.length - 1 && (
                    <div className={`absolute left-4 top-10 bottom-[-24px] w-0.5 ${status === 'completed' ? 'bg-forest-500' : 'bg-earth-200 dark:bg-earth-800'}`} />
                )}
                
                {/* Node Icon */}
                <div className={`absolute left-0 top-1 h-8 w-8 rounded-full border-2 flex items-center justify-center bg-white dark:bg-earth-950 z-10
                    ${status === 'completed' ? 'border-forest-500 text-forest-500' : 
                      status === 'unlocked' ? 'border-terracotta-500 text-terracotta-500 shadow-[0_0_10px_rgba(208,82,56,0.3)]' : 
                    'border-earth-300 text-earth-300 dark:border-earth-700 dark:text-earth-700'}`}
                >
                    {status === 'completed' && <CheckCircle2 className="h-5 w-5" />}
                    {status === 'unlocked' && <Play className="h-4 w-4 ml-0.5" />}
                    {status === 'locked' && <Lock className="h-4 w-4" />}
                </div>

                <Card 
                    hoverable={status !== 'locked'} 
                    className={`p-5 transition-all ${status === 'locked' ? 'opacity-60 grayscale' : ''} ${status === 'unlocked' ? 'border-terracotta-200 dark:border-terracotta-900/50' : ''}`}
                    onClick={() => status !== 'locked' && navigate(`/lesson/${lesson.id}`)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-earth-500 uppercase tracking-wide mb-1">Lesson {idx + 1}</p>
                      <h3 className="font-serif text-xl font-bold text-earth-900 dark:text-earth-100">{lesson.title}</h3>
                    </div>
                      {status === 'unlocked' && (
                      <Button size="sm">Start</Button>
                    )}
                      {status === 'completed' && (
                      <Button size="sm" variant="ghost">Review</Button>
                    )}
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>

            <div className="mt-10 space-y-4">
              <div className="flex items-center gap-2 text-forest-700 dark:text-forest-300 font-semibold uppercase text-xs tracking-[0.2em]">
                <Files className="h-4 w-4" /> Module Quizzes
              </div>

              {quizzes.length > 0 ? (
                <div className="grid gap-4 md:grid-cols-2">
                  {quizzes.map((quiz) => (
                    <Card key={quiz.id} className="border-forest-200 dark:border-forest-900/50 bg-forest-50/60 dark:bg-forest-900/10">
                      <div className="flex h-full flex-col justify-between gap-6">
                        <div>
                          <div className="flex items-center gap-2 mb-2 text-forest-700 dark:text-forest-300 text-xs font-semibold uppercase tracking-[0.2em]">
                            <Sparkles className="h-4 w-4" /> Quiz
                          </div>
                          <h3 className="font-serif text-2xl font-bold text-earth-900 dark:text-earth-50">{quiz.title}</h3>
                          <p className="text-earth-600 dark:text-earth-400 mt-2">Review the module lessons, then take this quiz to earn XP and unlock the next step in the journey.</p>
                        </div>
                        <div className="flex items-center justify-between gap-4">
                          <Badge variant="xp">Passing score {quiz.passing_score ?? 70}%</Badge>
                          <Button size="lg" onClick={() => startQuiz(quiz.id)} disabled={lessons.length === 0}>
                            Take Quiz
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card className="border-dashed border-earth-200 bg-white/60 text-earth-600 dark:border-earth-800 dark:bg-earth-900/20 dark:text-earth-300">
                  No quizzes are available for this module yet.
                </Card>
              )}
            </div>
        </div>
      </div>
    </div>
  );
};
