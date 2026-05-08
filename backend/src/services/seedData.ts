export const seedModules = [
  {
    slug: 'herbal-medicine',
    title: 'Herbal Medicine',
    description: 'The healing properties of native flora and roots.',
    difficulty: 'Intermediate',
    xp_reward: 450,
    category: 'Medicine',
    estimated_time: '3h',
    hero_story: 'The village pharmacy in a single tree.',
  },
  {
    slug: 'traditional-farming',
    title: 'Traditional Farming',
    description: 'Sustainable agriculture practices based on ancient rhythms.',
    difficulty: 'Beginner',
    xp_reward: 500,
    category: 'Agriculture',
    estimated_time: '2h',
    hero_story: 'Land, water, and seasons in balance.',
  },
  {
    slug: 'ancient-water-conservation',
    title: 'Ancient Water Conservation',
    description: 'Stepwells, rainwater harvesting, and desert survival.',
    difficulty: 'Intermediate',
    xp_reward: 600,
    category: 'Engineering',
    estimated_time: '4h',
    hero_story: 'When the monsoon came, the villages were ready.',
  },
  {
    slug: 'folk-stories-morals',
    title: 'Folk Stories & Morals',
    description: 'Oral traditions passed down generations for moral education.',
    difficulty: 'Beginner',
    xp_reward: 300,
    category: 'Culture',
    estimated_time: '1h',
    hero_story: 'Memory carried by the voice of the elders.',
  },
  {
    slug: 'traditional-crafts',
    title: 'Traditional Crafts',
    description: 'Pottery, weaving, and sustainable material crafting.',
    difficulty: 'Advanced',
    xp_reward: 700,
    category: 'Arts',
    estimated_time: '5h',
    hero_story: 'Craft as inheritance, not decoration.',
  },
  {
    slug: 'astronomy-navigation',
    title: 'Astronomy & Navigation',
    description: 'Reading the stars without modern instruments.',
    difficulty: 'Advanced',
    xp_reward: 800,
    category: 'Science',
    estimated_time: '4h',
    hero_story: 'The sky as a map and a calendar.',
  },
]

export const seedLessons = [
  {
    moduleSlug: 'herbal-medicine',
    title: 'Introduction to Neem',
    content: 'Neem is a traditional medicinal tree used for skin, immunity, and oral health.',
    order_index: 1,
  },
  {
    moduleSlug: 'herbal-medicine',
    title: 'Extracting Neem Oil',
    content: 'Cold-pressed neem oil is used for topical care and household protection.',
    order_index: 2,
  },
  {
    moduleSlug: 'herbal-medicine',
    title: 'Neem in Agriculture',
    content: 'Neem-based pest control reduces chemical dependence in farming.',
    order_index: 3,
  },
  {
    moduleSlug: 'herbal-medicine',
    title: 'Final Assessment',
    content: 'Review the uses, preparation, and precautions of neem remedies.',
    order_index: 4,
  },
  {
    moduleSlug: 'traditional-farming',
    title: 'Seasonal Cropping',
    content: 'Ancient systems aligned crops with rainfall and soil cycles.',
    order_index: 1,
  },
  {
    moduleSlug: 'traditional-farming',
    title: 'Composting and Soil Health',
    content: 'Farmers used organic waste to restore fertility over time.',
    order_index: 2,
  },
  {
    moduleSlug: 'traditional-farming',
    title: 'Seed Saving',
    content: 'Seed selection preserved resilience across generations.',
    order_index: 3,
  },
  {
    moduleSlug: 'traditional-farming',
    title: 'Assessment',
    content: 'Apply the principles of regenerative farming in local contexts.',
    order_index: 4,
  },
]

export const seedQuizzes = [
  {
    moduleSlug: 'herbal-medicine',
    title: 'Herbal Medicine Basics',
    passing_score: 70,
  },
  {
    moduleSlug: 'traditional-farming',
    title: 'Farming Foundations',
    passing_score: 70,
  },
]

export const seedQuizQuestions = [
  {
    quizTitle: 'Herbal Medicine Basics',
    question: 'Which ingredient improves curcumin absorption?',
    options: ['Black pepper', 'Salt', 'Rice', 'Lemon'],
    correct_answer: 'Black pepper',
    order_index: 1,
  },
  {
    quizTitle: 'Herbal Medicine Basics',
    question: 'What is a common use of neem?',
    options: ['Skin care', 'Metal polishing', 'Painting walls', 'Fuel only'],
    correct_answer: 'Skin care',
    order_index: 2,
  },
  {
    quizTitle: 'Farming Foundations',
    question: 'Why was seasonal cropping important?',
    options: ['It ignored rainfall', 'It matched climate cycles', 'It needed more chemicals', 'It reduced biodiversity'],
    correct_answer: 'It matched climate cycles',
    order_index: 1,
  },
  {
    quizTitle: 'Farming Foundations',
    question: 'What does composting improve?',
    options: ['Soil fertility', 'Plastic production', 'Phone battery life', 'Concrete strength'],
    correct_answer: 'Soil fertility',
    order_index: 2,
  },
]

export const seedAchievements = [
  {
    slug: 'first-harvest',
    title: 'First Harvest',
    description: 'Complete your first agricultural lesson.',
    xp_reward: 100,
  },
  {
    slug: 'village-elder',
    title: 'Village Elder',
    description: 'Reach level 10 and guide others.',
    xp_reward: 250,
  },
  {
    slug: 'healer-apprentice',
    title: 'Healer Apprentice',
    description: 'Master the basics of herbal medicine.',
    xp_reward: 150,
  },
  {
    slug: 'water-saver',
    title: 'Water Saver',
    description: 'Learn about ancient stepwells.',
    xp_reward: 150,
  },
]

export const seedUsers = [
  {
    name: 'Sita Devi',
    email: 'sita@tradition.dev',
    password: 'Password123!',
    avatar_url: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&q=80&w=150',
    xp_points: 12500,
    level: 25,
    streak: 31,
  },
  {
    name: 'Ravi Kumar',
    email: 'ravi@tradition.dev',
    password: 'Password123!',
    avatar_url: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&q=80&w=150',
    xp_points: 11200,
    level: 23,
    streak: 22,
  },
  {
    name: 'Priya Sharma',
    email: 'priya@tradition.dev',
    password: 'Password123!',
    avatar_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=150',
    xp_points: 10800,
    level: 22,
    streak: 28,
  },
  {
    name: 'Arjun Singh',
    email: 'arjun@tradition.dev',
    password: 'Password123!',
    avatar_url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=150',
    xp_points: 9500,
    level: 20,
    streak: 17,
  },
  {
    name: 'Anand Traveler',
    email: 'anand@tradition.dev',
    password: 'Password123!',
    avatar_url: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&q=80&w=150',
    xp_points: 2450,
    level: 5,
    streak: 12,
  },
]