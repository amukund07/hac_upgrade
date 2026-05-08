import { Trophy } from 'lucide-react'
import { Badge } from '../ui/Badge'

interface QuizNavbarProps {
  title: string
  level?: number
}

export const QuizNavbar = ({ title, level }: QuizNavbarProps) => {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-terracotta-500/15 bg-earth-950/95 px-6 py-4 backdrop-blur-sm">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-earth-400">Quiz Mode</p>
        <h1 className="font-serif text-2xl font-bold text-cream">{title}</h1>
      </div>

      <Badge variant="level" className="gap-2 border-terracotta-500/20 bg-terracotta-500/15 text-cream">
        <Trophy className="h-4 w-4" />
        Level {level ?? 1}
      </Badge>
    </div>
  )
}