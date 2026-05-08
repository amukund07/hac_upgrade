import { forwardRef, type HTMLAttributes } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/utils';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean;
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, hoverable, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'rounded-2xl border border-earth-100 bg-white/80 p-6 shadow-sm backdrop-blur-md transition-all dark:border-earth-800 dark:bg-earth-900/40',
          hoverable && 'hover:-translate-y-1 hover:shadow-lg hover:shadow-earth-200/50 dark:hover:shadow-earth-900/50 cursor-pointer',
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
Card.displayName = 'Card';

export const MotionCard = motion.create(Card);
