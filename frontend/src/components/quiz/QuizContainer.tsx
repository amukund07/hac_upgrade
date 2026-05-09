import type { ReactNode } from 'react'
import { cn } from '../../utils/utils'

interface QuizContainerProps {
  children: ReactNode
  className?: string
}

export const QuizContainer = ({ children, className }: QuizContainerProps) => {
  return (
    <div className={cn('relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,rgba(255,220,165,0.12),transparent_28%),linear-gradient(180deg,rgba(22,18,16,1)_0%,rgba(35,23,17,1)_50%,rgba(18,12,10,1)_100%)] text-cream', className)}>
      <div className="pointer-events-none absolute inset-0 opacity-90">
        <div className="absolute left-0 top-0 h-72 w-72 rounded-full bg-amber-400/10 blur-3xl" />
        <div className="absolute right-0 top-20 h-80 w-80 rounded-full bg-terracotta-500/10 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-96 w-96 rounded-full bg-forest-500/10 blur-3xl" />
      </div>
      <div className="relative z-10">{children}</div>
    </div>
  )
}