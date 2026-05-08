import { forwardRef } from 'react';
import { motion, type HTMLMotionProps } from 'framer-motion';
import { cn } from '../../utils/utils';

type ButtonProps = HTMLMotionProps<"button"> & {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, children, ...props }, ref) => {

    const variants = {
      primary: 'bg-earth-500 text-white hover:bg-earth-600 shadow-lg shadow-earth-500/30',
      secondary: 'bg-forest-500 text-white hover:bg-forest-600 shadow-lg shadow-forest-500/30',
      outline: 'border-2 border-earth-500 text-earth-700 hover:bg-earth-50 dark:text-earth-300 dark:hover:bg-earth-900/50',
      ghost: 'hover:bg-earth-100 text-earth-700 dark:text-earth-300 dark:hover:bg-earth-900/50',
    };

    const sizes = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-5 py-2.5 text-base',
      lg: 'px-8 py-4 text-lg font-semibold',
    };

    return (
      <motion.button
        ref={ref}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={cn(
          'inline-flex items-center justify-center rounded-xl font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-earth-500/50 disabled:opacity-50 disabled:pointer-events-none',
          variants[variant],
          sizes[size],
          className
        )}
        disabled={isLoading || props.disabled}
        {...props}
      >
        {isLoading ? (
          <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        ) : null}
        {children as React.ReactNode}
      </motion.button>
    );
  }
);

Button.displayName = 'Button';
