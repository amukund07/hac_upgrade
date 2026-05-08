import { motion } from 'framer-motion'

export const FloatingParticles = () => {
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      {[...Array(10)].map((_, index) => (
        <motion.span
          key={index}
          className="absolute h-2.5 w-2.5 rounded-full bg-terracotta-500/15 blur-[1px]"
          initial={{ opacity: 0, y: 120 + index * 4, x: (index % 2 === 0 ? -1 : 1) * (20 + index * 6) }}
          animate={{
            opacity: [0, 1, 0.6, 0],
            y: [120 + index * 4, -140 - index * 12],
            x: [(index % 2 === 0 ? -1 : 1) * (20 + index * 6), (index % 2 === 0 ? 1 : -1) * (30 + index * 5)],
          }}
          transition={{ duration: 8 + index * 0.6, repeat: Infinity, delay: index * 0.35, ease: 'easeInOut' }}
          style={{ left: `${8 + index * 9}%`, bottom: '-8%' }}
        />
      ))}
    </div>
  )
}