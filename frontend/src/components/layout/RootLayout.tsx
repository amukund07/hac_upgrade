import { Outlet, useLocation } from 'react-router-dom';
import { FloatingBackground } from '../ui/FloatingBackground';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import { ChatPopup } from '../chat/ChatPopup';
import { AnimatePresence, motion } from 'framer-motion';

export const RootLayout = () => {
  const location = useLocation();
  const isDashboardRoute = 
    location.pathname.includes('/dashboard') || 
    location.pathname.includes('/modules') || 
    location.pathname.includes('/profile') || 
    location.pathname.includes('/leaderboard') || 
    location.pathname.includes('/chat');

  return (
    <FloatingBackground>
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        {isDashboardRoute && <Sidebar />}
        <main className="flex-1 overflow-y-auto relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="h-full"
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
          <ChatPopup />
        </main>
      </div>
    </FloatingBackground>
  );
};
