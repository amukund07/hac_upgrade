import { forwardRef, type HTMLAttributes } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/utils';

interface ProgressBarProps extends HTMLAttributes<HTMLDivElement> {
  progress: number;
  variant?: 'default' | 'success' | 'warning';
  showLabel?: boolean;
}

export const ProgressBar = forwardRef<HTMLDivElement, ProgressBarProps>(
  ({ className, progress, variant = 'default', showLabel = false, ...props }, ref) => {

    const variants = {
      default: 'bg-forest-500',
      success: 'bg-earth-500',
      warning: 'bg-terracotta-500',
    };

    return (
      <div className={cn('w-full', className)} ref={ref} {...props}>
        {showLabel && (
          <div className="mb-1.5 flex justify-between text-xs font-medium text-earth-600 dark:text-earth-400">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
        )}
        <div className="h-2.5 w-full overflow-hidden rounded-full bg-earth-100 dark:bg-earth-800">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(Math.max(progress, 0), 100)}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className={cn('h-full rounded-full', variants[variant])}
          />
        </div>
      </div>
    );
  }
);
ProgressBar.displayName = 'ProgressBar';
