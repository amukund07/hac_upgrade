import { forwardRef, type HTMLAttributes } from 'react';
import { cn } from '../../utils/utils';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'xp' | 'level' | 'category' | 'achievement';
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'category', children, ...props }, ref) => {

    const variants = {
      xp: 'bg-terracotta-500/10 text-terracotta-600 border-terracotta-500/20 dark:bg-terracotta-500/20 dark:text-terracotta-400',
      level: 'bg-forest-500/10 text-forest-600 border-forest-500/20 dark:bg-forest-500/20 dark:text-forest-400',
      category: 'bg-earth-100 text-earth-700 border-earth-200 dark:bg-earth-800 dark:text-earth-300 dark:border-earth-700',
      achievement: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20 dark:bg-yellow-500/20 dark:text-yellow-400',
    };

    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
          variants[variant],
          className
        )}
        {...props}
      >
        {children}
      </span>
    );
  }
);
Badge.displayName = 'Badge';
