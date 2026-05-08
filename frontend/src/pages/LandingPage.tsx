import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Leaf, BookOpen, MessageSquare, Trophy } from 'lucide-react';

export const LandingPage = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Ancestral Wisdom',
      description: 'Learn ancient practices like traditional farming, herbal medicine, and sustainable living.',
      icon: BookOpen,
      color: 'text-forest-600',
      bg: 'bg-forest-100 dark:bg-forest-900/50',
    },
    {
      title: 'Gamified Learning',
      description: 'Earn XP, collect badges, and climb the leaderboard as you master new skills.',
      icon: Trophy,
      color: 'text-terracotta-600',
      bg: 'bg-terracotta-100 dark:bg-terracotta-900/50',
    },
    {
      title: 'Elder Spirit Guide',
      description: 'Interact with our AI chatbot trained on cultural folklore and traditional knowledge.',
      icon: MessageSquare,
      color: 'text-earth-600',
      bg: 'bg-earth-100 dark:bg-earth-900/50',
    },
  ];

  return (
    <div className="flex flex-col items-center justify-center pt-20 pb-32">
      {/* Hero Section */}
      <section className="container mx-auto px-4 md:px-6 text-center max-w-4xl mt-12 mb-24">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-forest-100/80 shadow-inner dark:bg-forest-900/40">
            <Leaf className="h-10 w-10 text-forest-600 dark:text-forest-400" />
          </div>
          <h1 className="mb-6 font-serif text-5xl font-bold tracking-tight text-earth-900 dark:text-earth-50 md:text-7xl">
            Reconnect with the <br className="hidden md:block" />
            <span className="text-forest-600 dark:text-forest-400">Roots of Wisdom</span>
          </h1>
          <p className="mx-auto mb-10 max-w-2xl text-lg text-earth-600 dark:text-earth-300 md:text-xl leading-relaxed">
            A gamified journey into traditional knowledge. Discover forgotten arts, sustainable practices, and cultural folklore through immersive storytelling.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button size="lg" onClick={() => navigate('/signup')} className="w-full sm:w-auto text-lg px-10">
              Start Learning
            </Button>
            <Button variant="outline" size="lg" onClick={() => navigate('/modules')} className="w-full sm:w-auto text-lg px-10">
              Explore Modules
            </Button>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 md:px-6 mb-24">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="grid gap-8 md:grid-cols-3"
        >
          {features.map((feature, idx) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.2, duration: 0.6 }}
            >
              <Card hoverable className="h-full flex flex-col items-center text-center p-8">
                <div className={`mb-6 flex h-16 w-16 items-center justify-center rounded-2xl ${feature.bg} ${feature.color}`}>
                  <feature.icon className="h-8 w-8" />
                </div>
                <h3 className="mb-3 font-serif text-2xl font-semibold text-earth-900 dark:text-earth-100">
                  {feature.title}
                </h3>
                <p className="text-earth-600 dark:text-earth-400">
                  {feature.description}
                </p>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Quote Section */}
      <section className="container mx-auto px-4 md:px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mx-auto max-w-3xl rounded-3xl bg-earth-800 p-10 text-center shadow-xl dark:bg-earth-900"
        >
          <p className="font-serif text-2xl italic text-earth-100 md:text-3xl leading-snug">
            "A people without the knowledge of their past history, origin and culture is like a tree without roots."
          </p>
          <div className="mt-6 flex items-center justify-center gap-3">
            <div className="h-1 w-12 bg-terracotta-500 rounded-full" />
            <span className="text-sm font-medium uppercase tracking-wider text-earth-300">Marcus Garvey</span>
            <div className="h-1 w-12 bg-terracotta-500 rounded-full" />
          </div>
        </motion.div>
      </section>
    </div>
  );
};
