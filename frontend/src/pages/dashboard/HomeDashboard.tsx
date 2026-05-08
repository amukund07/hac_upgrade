import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Play, Award, Flame } from 'lucide-react'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { ProgressBar } from '../../components/ui/ProgressBar'
import { useAuth } from '../../context/AuthContext'
import { getAllModules, type LearningModule } from '../../services/moduleService'
import { getUserModuleProgress } from '../../services/progressService'

export const HomeDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth()
  const [modules, setModules] = useState<Array<LearningModule & { progress: number }>>([])

  useEffect(() => {
    const loadDashboard = async () => {
      const modulesResult = await getAllModules()
      const sourceModules = modulesResult.data ?? []

      if (!user) {
        setModules(sourceModules.map((module) => ({ ...module, progress: 0 })))
        return
      }

      const modulesWithProgress = await Promise.all(
        sourceModules.map(async (module) => {
          const progressResult = await getUserModuleProgress(user.id, module.id)
          return {
            ...module,
            progress: progressResult.data?.progress_percentage ?? 0,
          }
        }),
      )

      setModules(modulesWithProgress)
    }

    void loadDashboard()
  }, [user])

  const continueModule = useMemo(() => modules.find((module) => module.progress < 100) ?? modules[0], [modules])
  const recommendedModules = useMemo(() => modules.slice(0, 3), [modules])

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
      {/* Welcome Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:items-end justify-between gap-4"
      >
        <div>
          <h1 className="font-serif text-4xl font-bold text-earth-900 dark:text-earth-50">Welcome back, {user?.name ?? 'Traveler'}</h1>
          <p className="mt-2 text-earth-600 dark:text-earth-400">The village elders have new knowledge to share with you.</p>
        </div>
        <div className="flex gap-4">
          <Card className="flex items-center gap-3 p-4 shrink-0">
            <div className="rounded-full bg-yellow-100 p-2 dark:bg-yellow-900/50">
              <Award className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase text-earth-500">Total XP</p>
              <p className="text-xl font-bold text-earth-900 dark:text-earth-100">{user?.xp_points?.toLocaleString() ?? '0'}</p>
            </div>
          </Card>
          <Card className="flex items-center gap-3 p-4 shrink-0">
            <div className="rounded-full bg-terracotta-100 p-2 dark:bg-terracotta-900/50">
              <Flame className="h-6 w-6 text-terracotta-600 dark:text-terracotta-400" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase text-earth-500">Day Streak</p>
              <p className="text-xl font-bold text-earth-900 dark:text-earth-100">{user?.streak ?? 0}</p>
            </div>
          </Card>
        </div>
      </motion.div>

      {/* Continue Learning */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h2 className="font-serif text-2xl font-semibold text-earth-900 dark:text-earth-100 mb-4">Continue Learning</h2>
        <Card hoverable className="flex flex-col md:flex-row gap-6 items-center p-6 bg-gradient-to-r from-forest-50 to-white dark:from-forest-900/20 dark:to-earth-900/40" onClick={() => continueModule && navigate(`/modules/${continueModule.id}`)}>
          <div className="flex-1 w-full space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Badge variant="category">{continueModule?.category ?? 'Learning'}</Badge>
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-forest-100/50 dark:bg-forest-900/50 border border-forest-200 dark:border-forest-800">
                  <Play className="h-3 w-3 text-forest-600 dark:text-forest-400" />
                  <span className="text-[10px] font-bold uppercase tracking-wider text-forest-700 dark:text-forest-300">Resume Lesson</span>
                </div>
              </div>
              <Badge variant="xp">+{continueModule?.xp_reward ?? 0} XP</Badge>
            </div>
            <h3 className="font-serif text-2xl font-bold text-earth-900 dark:text-earth-100">{continueModule?.title ?? 'Loading your next lesson...'}</h3>
            <p className="text-earth-600 dark:text-earth-400 line-clamp-2 italic font-serif">{continueModule?.hero_story ?? 'Your next lesson is being loaded from the database.'}</p>
            <div className="pt-2">
              <ProgressBar progress={continueModule?.progress ?? 0} variant="success" showLabel />
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Recommended Modules */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-serif text-2xl font-semibold text-earth-900 dark:text-earth-100">Recommended for You</h2>
          <button onClick={() => navigate('/modules')} className="text-sm font-semibold text-forest-600 hover:text-forest-700 dark:text-forest-400">View All</button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recommendedModules.map((mod) => (
            <Card hoverable key={mod.id} className="flex flex-col gap-4 cursor-pointer" onClick={() => navigate(`/modules/${mod.id}`)}>
              <div className="flex-1 space-y-3">
                <Badge variant="category">{mod.category}</Badge>
                <h3 className="font-serif text-lg font-bold text-earth-900 dark:text-earth-100">{mod.title}</h3>
                <p className="text-sm text-earth-600 dark:text-earth-400">{mod.description}</p>
              </div>
              <ProgressBar progress={mod.progress} variant={mod.progress === 100 ? 'default' : 'warning'} />
            </Card>
          ))}
        </div>
      </motion.div>
    </div>
  );
};
