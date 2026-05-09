import { motion } from 'framer-motion'
import { CheckCircle2, XCircle, Circle } from 'lucide-react'
import { cn } from '../../utils/utils'

interface OptionButtonProps {
  label: string
  state: 'idle' | 'selected' | 'correct' | 'wrong'
  disabled?: boolean
  onClick: () => void
}

export const OptionButton = ({ label, state, disabled, onClick }: OptionButtonProps) => {
  const getStyles = () => {
    switch (state) {
      case 'selected':
        return 'border-2 border-terracotta-500 bg-terracotta-500/15 text-white shadow-[0_0_20px_rgba(200,104,73,0.25)]'
      case 'correct':
        return 'border-2 border-emerald-500 bg-emerald-500/15 text-emerald-50 shadow-[0_0_25px_rgba(16,185,129,0.3)]'
      case 'wrong':
        return 'border-2 border-rose-500 bg-rose-500/15 text-rose-50 shadow-[0_0_15px_rgba(244,63,94,0.2)]'
      default:
        return 'border-2 border-white/30 bg-white/8 text-white hover:border-white/50 hover:bg-white/15'
    }
  }

  const getIcon = () => {
    switch (state) {
      case 'correct':
        return <CheckCircle2 className="h-5 w-5 text-emerald-400" />
      case 'wrong':
        return <XCircle className="h-5 w-5 text-rose-400" />
      case 'selected':
        return <Circle className="h-5 w-5 fill-terracotta-500 text-terracotta-500" />
      default:
        return <Circle className="h-5 w-5 text-white/20" />
    }
  }

  return (
    <motion.button
      whileHover={!disabled ? { x: 6, scale: 1.02 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'group flex w-full items-center justify-between gap-3 rounded-xl border px-4 py-4 md:px-6 md:py-6 md:rounded-2xl transition-all duration-200 font-medium text-base md:text-lg',
        getStyles(),
        disabled && state === 'idle' && 'opacity-50',
        !disabled && 'cursor-pointer'
      )}
    >
      <span className="text-base md:text-lg font-medium">{label}</span>
      <div className="flex-shrink-0 transition-transform duration-300 group-hover:scale-110">
        {getIcon()}
      </div>
    </motion.button>
  )
}
