import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { Leaf, UserPlus } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { useAuth } from '../../context/AuthContext';

export const SignupPage = () => {
  const navigate = useNavigate();
  const { signUp } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await signUp({ name, email, password });
      navigate('/dashboard');
    } catch (signupError) {
      setError(signupError instanceof Error ? signupError.message : 'Unable to sign up');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card className="p-8">
          <div className="mb-8 flex flex-col items-center text-center">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-terracotta-100 text-terracotta-600 dark:bg-terracotta-900/50 dark:text-terracotta-400 shadow-inner">
              <Leaf className="h-8 w-8" />
            </div>
            <h2 className="font-serif text-3xl font-bold text-earth-900 dark:text-earth-50">Join the Village</h2>
            <p className="mt-2 text-earth-600 dark:text-earth-400">Start your journey into traditional wisdom.</p>
          </div>

          <form onSubmit={handleSignup} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-earth-700 dark:text-earth-300">Username</label>
              <input
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                required
                className="w-full rounded-xl border border-earth-200 bg-earth-50/50 px-4 py-3 text-earth-900 outline-none transition-all focus:border-earth-500 focus:ring-2 focus:ring-earth-500/20 dark:border-earth-700 dark:bg-earth-800/50 dark:text-earth-100"
                placeholder="villager123"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-earth-700 dark:text-earth-300">Email</label>
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                className="w-full rounded-xl border border-earth-200 bg-earth-50/50 px-4 py-3 text-earth-900 outline-none transition-all focus:border-earth-500 focus:ring-2 focus:ring-earth-500/20 dark:border-earth-700 dark:bg-earth-800/50 dark:text-earth-100"
                placeholder="elder@village.com"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-earth-700 dark:text-earth-300">Password</label>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                className="w-full rounded-xl border border-earth-200 bg-earth-50/50 px-4 py-3 text-earth-900 outline-none transition-all focus:border-earth-500 focus:ring-2 focus:ring-earth-500/20 dark:border-earth-700 dark:bg-earth-800/50 dark:text-earth-100"
                placeholder="••••••••"
              />
            </div>
            {error && <p className="text-sm text-red-500">{error}</p>}
            <Button type="submit" className="w-full mt-6" size="lg" variant="secondary">
              <UserPlus className="mr-2 h-5 w-5" /> {isSubmitting ? 'Creating Account...' : 'Sign Up'}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-earth-600 dark:text-earth-400">
            Already a member?{' '}
            <Link to="/login" className="font-semibold text-earth-800 hover:text-forest-600 dark:text-earth-200 transition-colors">
              Sign In
            </Link>
          </div>
        </Card>
      </motion.div>
    </div>
  );
};
