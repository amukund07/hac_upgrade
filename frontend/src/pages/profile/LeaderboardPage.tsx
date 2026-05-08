import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Trophy } from 'lucide-react'
import { Card } from '../../components/ui/Card'
import { useAuth } from '../../context/AuthContext'
import { getLeaderboard, type LeaderboardEntry } from '../../services/leaderboardService'

export const LeaderboardPage = () => {
  const { user } = useAuth()
  const [leaders, setLeaders] = useState<LeaderboardEntry[]>([])

  useEffect(() => {
    const loadLeaderboard = async () => {
      const leaderboardResult = await getLeaderboard()
      const ordered = (leaderboardResult.data ?? []).map((entry, index) => ({
        ...entry,
        rank: index + 1,
      }))
      setLeaders(ordered)
    }

    void loadLeaderboard()
  }, [])

  return (
    <div className="p-6 md:p-8 max-w-4xl mx-auto space-y-8 pb-24">
      {/* Header */}
      <div className="text-center space-y-4">
        <motion.div 
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", bounce: 0.5 }}
          className="mx-auto w-20 h-20 bg-yellow-100 dark:bg-yellow-900/50 rounded-full flex items-center justify-center shadow-inner"
        >
          <Trophy className="h-10 w-10 text-yellow-500" />
        </motion.div>
        <h1 className="font-serif text-3xl md:text-4xl font-bold text-earth-900 dark:text-earth-50">Village Leaders</h1>
        <p className="text-earth-600 dark:text-earth-400 max-w-lg mx-auto">
          The most dedicated learners preserving our cultural heritage.
        </p>
      </div>

      {/* List */}
      <div className="space-y-4 mt-12">
        {leaders.map((leader, idx) => (
          <motion.div
            key={leader.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            <Card className={`flex items-center gap-4 p-4 md:p-6 transition-all ${user?.id === leader.id ? 'border-terracotta-400 shadow-md ring-1 ring-terracotta-400/50 bg-terracotta-50/50 dark:bg-terracotta-900/10' : ''}`}>
              <div className={`w-8 font-bold text-lg text-center ${
                idx + 1 === 1 ? 'text-yellow-500' : 
                idx + 1 === 2 ? 'text-gray-400' : 
                idx + 1 === 3 ? 'text-orange-400' : 'text-earth-400'
              }`}>
                #{idx + 1}
              </div>
              
              <div className="relative">
                <img src={leader.avatar_url || 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&q=80&w=150'} alt={leader.name} className="w-12 h-12 rounded-full object-cover border-2 border-white dark:border-earth-800 shadow-sm" />
                {idx + 1 === 1 && (
                  <div className="absolute -top-3 -right-2 text-xl">👑</div>
                )}
              </div>
              
              <div className="flex-1">
                <h3 className="font-bold text-earth-900 dark:text-earth-100">{leader.name} {user?.id === leader.id && <span className="text-xs font-normal text-terracotta-600 ml-2">(You)</span>}</h3>
                <p className="text-sm text-earth-500">Level {leader.level ?? 1}</p>
              </div>
              
              <div className="text-right">
                <p className="font-bold text-earth-900 dark:text-earth-100">{leader.xp_points.toLocaleString()}</p>
                <p className="text-xs font-semibold text-earth-400 uppercase tracking-wide">XP</p>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
