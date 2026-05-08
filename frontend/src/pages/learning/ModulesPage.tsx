import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Filter, BookOpen } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { ProgressBar } from '../../components/ui/ProgressBar'
import { useAuth } from '../../context/AuthContext'
import { getAllModules, type LearningModule } from '../../services/moduleService'
import { getUserModuleProgress } from '../../services/progressService'

type ModuleCard = LearningModule & {
  progress: number
}

export const ModulesPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth()
  const [searchTerm, setSearchTerm] = useState('')
  const [modules, setModules] = useState<ModuleCard[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadModules = async () => {
      setIsLoading(true)

      const modulesResult = await getAllModules()
      const sourceModules = modulesResult.data ?? []

      if (!user) {
        setModules(sourceModules.map((module) => ({ ...module, progress: 0 })))
        setIsLoading(false)
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
      setIsLoading(false)
    }

    void loadModules()
  }, [user])

  const filteredModules = useMemo(() => {
    const query = searchTerm.trim().toLowerCase()
    if (!query) {
      return modules
    }

    return modules.filter((module) => (
      module.title.toLowerCase().includes(query)
      || module.description.toLowerCase().includes(query)
      || (module.category ?? '').toLowerCase().includes(query)
    ))
  }, [modules, searchTerm])

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
      {/* Header & Search */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="font-serif text-3xl font-bold text-earth-900 dark:text-earth-50">Learning Modules</h1>
          <p className="mt-2 text-earth-600 dark:text-earth-400">Discover and master the ways of the ancestors.</p>
        </div>
        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-earth-400" />
            <input
              type="text"
              placeholder="Search knowledge..."
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              className="w-full rounded-xl border border-earth-200 bg-white/50 pl-10 pr-4 py-2 text-sm outline-none focus:border-earth-500 focus:ring-2 focus:ring-earth-500/20 dark:border-earth-700 dark:bg-earth-900/50 dark:text-earth-100"
            />
          </div>
          <button className="flex items-center justify-center rounded-xl border border-earth-200 bg-white/50 p-2.5 text-earth-600 hover:bg-earth-100 dark:border-earth-700 dark:bg-earth-900/50 dark:text-earth-300 dark:hover:bg-earth-800">
            <Filter className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Grid */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={{
          hidden: { opacity: 0 },
          visible: { opacity: 1, transition: { staggerChildren: 0.1 } },
        }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {isLoading && (
          <div className="col-span-full rounded-2xl border border-dashed border-earth-200 bg-white/50 p-8 text-center text-earth-500 dark:border-earth-800 dark:bg-earth-900/20">
            Loading modules from the database...
          </div>
        )}

        {!isLoading && filteredModules.map((mod) => (
          <motion.div
            key={mod.id}
            variants={{
              hidden: { opacity: 0, y: 20 },
              visible: { opacity: 1, y: 0 },
            }}
          >
            <Card hoverable className="h-full flex flex-col group" onClick={() => navigate(`/modules/${mod.id}`)}>
              <div className="flex-1 flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <Badge variant="category" className="w-fit">{mod.category ?? 'Learning'}</Badge>
                  <div className="flex items-center gap-2">
                    <span className="flex items-center text-[10px] font-bold uppercase tracking-wider text-earth-500 dark:text-earth-400">
                      <BookOpen className="h-3 w-3 mr-1" /> {mod.estimated_time ?? '—'}
                    </span>
                    <Badge variant="xp" className="bg-terracotta-500/10 text-terracotta-600 border-terracotta-200 dark:bg-terracotta-500/20 dark:text-terracotta-400 dark:border-terracotta-800">
                      +{mod.xp_reward} XP
                    </Badge>
                  </div>
                </div>
                <h3 className="font-serif text-xl font-bold text-earth-900 dark:text-earth-100 mb-2">{mod.title}</h3>
                <p className="text-sm text-earth-600 dark:text-earth-400 mb-6 flex-1">{mod.description}</p>
                <ProgressBar progress={mod.progress} showLabel variant={mod.progress === 100 ? 'default' : 'warning'} />
              </div>
            </Card>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
};
