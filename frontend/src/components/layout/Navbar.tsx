import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Leaf, Menu, User, LogIn } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Navbar = () => {
  const location = useLocation();
  const { user } = useAuth();
  const isAuthPage = location.pathname.includes('/login') || location.pathname.includes('/signup');
  const isLandingPage = location.pathname === '/';
  const isAuthenticated = Boolean(user) && !isLandingPage;

  if (isAuthPage) return null;

  return (
    <header className="sticky top-0 z-40 w-full border-b border-earth-200/50 bg-white/60 backdrop-blur-md dark:border-earth-800/50 dark:bg-earth-900/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4 md:px-6">
        <div className="flex items-center gap-2">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-forest-100 text-forest-600 transition-colors group-hover:bg-forest-200 dark:bg-forest-900/50 dark:text-forest-400">
              <Leaf className="h-6 w-6" />
              <motion.div
                className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-terracotta-500"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 2 }}
              />
            </div>
            <span className="font-serif text-xl font-bold tracking-tight text-earth-900 dark:text-earth-50">
              Tradition
            </span>
          </Link>
        </div>

        <nav className="hidden md:flex items-center gap-6">
          <Link to="/modules" className="text-sm font-medium text-earth-600 hover:text-forest-600 dark:text-earth-300 dark:hover:text-forest-400 transition-colors">
            Learn
          </Link>
          <Link to="/leaderboard" className="text-sm font-medium text-earth-600 hover:text-forest-600 dark:text-earth-300 dark:hover:text-forest-400 transition-colors">
            Leaderboard
          </Link>
        </nav>

        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <Link to="/profile" className="flex items-center gap-2 rounded-full border border-earth-200 bg-white px-3 py-1.5 hover:bg-earth-50 dark:border-earth-700 dark:bg-earth-800 dark:hover:bg-earth-700/80 transition-colors">
              <User className="h-4 w-4 text-earth-600 dark:text-earth-300" />
              <span className="text-sm font-medium text-earth-800 dark:text-earth-200">Level {user?.level ?? 1}</span>
            </Link>
          ) : (
            <Link to="/login" className="flex items-center gap-2 rounded-full bg-forest-600 px-4 py-2 text-sm font-medium text-white hover:bg-forest-700 transition-colors shadow-sm shadow-forest-600/20">
              <LogIn className="h-4 w-4" />
              Sign In
            </Link>
          )}
          <button className="md:hidden flex items-center justify-center rounded-md p-2 text-earth-600 hover:bg-earth-100 dark:text-earth-300 dark:hover:bg-earth-800">
            <Menu className="h-6 w-6" />
          </button>
        </div>
      </div>
    </header>
  );
};
