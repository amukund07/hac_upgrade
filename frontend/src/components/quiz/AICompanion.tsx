import { AnimatePresence, motion } from 'framer-motion'

interface AICompanionProps {
  emotion: 'neutral' | 'happy' | 'thinking' | 'encouraging'
  message?: string
}

export const AICompanion = ({ emotion, message }: AICompanionProps) => {
  const emoji = (() => {
    switch (emotion) {
      case 'happy':
        return '😊'
      case 'thinking':
        return '🤔'
      case 'encouraging':
        return '💫'
      default:
        return '🙏'
    }
  })()

  return (
    <motion.div initial={{ scale: 0, x: 20 }} animate={{ scale: 1, x: 0 }} className="hidden lg:flex flex-col items-end gap-3">
      <AnimatePresence mode="wait">
        {message && (
          <motion.div
            key={message}
            initial={{ opacity: 0, x: 10, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 10, scale: 0.9 }}
            className="max-w-xs rounded-2xl rounded-br-sm border border-terracotta-500/25 bg-earth-950/90 px-4 py-3 text-sm text-earth-100 shadow-xl"
          >
            {message}
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        className="flex h-16 w-16 items-center justify-center rounded-full border border-cream/20 bg-gradient-to-br from-terracotta-500 to-burnt-orange-500 text-3xl shadow-[0_8px_30px_rgba(200,104,73,0.3)]"
      >
        {emoji}
      </motion.div>
    </motion.div>
  )
}