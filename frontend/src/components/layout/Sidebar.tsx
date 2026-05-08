import { NavLink } from 'react-router-dom';
import { Home, BookOpen, Trophy, User } from 'lucide-react';
import { cn } from '../../utils/utils';

export const Sidebar = () => {
  const navItems = [
    { icon: Home, label: 'Home', path: '/dashboard' },
    { icon: BookOpen, label: 'Learn', path: '/modules' },
    { icon: Trophy, label: 'Leaderboard', path: '/leaderboard' },
    { icon: User, label: 'Profile', path: '/profile' },
  ];

  return (
    <aside className="hidden md:flex w-64 flex-col border-r border-earth-200/50 bg-white/50 backdrop-blur-md dark:border-earth-800/50 dark:bg-earth-900/30 p-4 shrink-0">
      <nav className="flex flex-col gap-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-forest-100 text-forest-700 dark:bg-forest-900/40 dark:text-forest-300 shadow-sm shadow-forest-200/20'
                  : 'text-earth-600 hover:bg-earth-100/50 hover:text-earth-900 dark:text-earth-400 dark:hover:bg-earth-800/50 dark:hover:text-earth-200'
              )
            }
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto rounded-2xl bg-earth-100 p-4 dark:bg-earth-800/50 border border-earth-200 dark:border-earth-700">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 shrink-0 rounded-full bg-terracotta-500/20 flex items-center justify-center">
            <span className="text-terracotta-600 font-bold dark:text-terracotta-400">🔥</span>
          </div>
          <div>
            <p className="text-sm font-semibold text-earth-900 dark:text-earth-100">12 Day Streak!</p>
            <p className="text-xs text-earth-500 dark:text-earth-400">Keep learning to grow.</p>
          </div>
        </div>
      </div>
    </aside>
  );
};
