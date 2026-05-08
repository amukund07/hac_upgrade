import { createBrowserRouter } from 'react-router-dom';
import { RootLayout } from '../components/layout/RootLayout';
import { LandingPage } from '../pages/LandingPage';
import { LoginPage } from '../pages/auth/LoginPage';
import { SignupPage } from '../pages/auth/SignupPage';
import { HomeDashboard } from '../pages/dashboard/HomeDashboard';
import { ModulesPage } from '../pages/learning/ModulesPage';
import { ModuleDetailsPage } from '../pages/learning/ModuleDetailsPage';
import { LessonPage } from '../pages/learning/LessonPage';
import { QuizPage } from '../pages/quiz/QuizPage';
import { AIChatbotPage } from '../pages/chat/AIChatbotPage';
import { ProfilePage } from '../pages/profile/ProfilePage';
import { LeaderboardPage } from '../pages/profile/LeaderboardPage';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';



export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <LandingPage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'signup', element: <SignupPage /> },
      {
        element: <ProtectedRoute />,
        children: [
          { path: 'dashboard', element: <HomeDashboard /> },
          { path: 'modules', element: <ModulesPage /> },
          { path: 'modules/:id', element: <ModuleDetailsPage /> },
          { path: 'lesson/:id', element: <LessonPage /> },
          { path: 'quiz/:id', element: <QuizPage /> },
          { path: 'profile', element: <ProfilePage /> },
          { path: 'leaderboard', element: <LeaderboardPage /> },
          { path: 'chat', element: <AIChatbotPage /> },
        ],
      },
    ],
  },
]);
