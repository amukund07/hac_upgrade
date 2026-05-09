import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles } from 'lucide-react'

interface XPAnimationProps {
  xp: number
}

export const XPAnimation = ({ xp }: XPAnimationProps) => {
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 10, scale: 0.8 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, scale: 0.5 }}
        className="flex items-center gap-1.5 rounded-full bg-amber-400/10 px-3 py-1 border border-amber-400/20"
      >
        <Sparkles className="h-3.5 w-3.5 text-amber-400 animate-pulse" />
        <span className="text-xs font-bold text-amber-400">+{xp} XP potential</span>
      </motion.div>
    </AnimatePresence>
  )
}
