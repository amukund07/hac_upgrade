export const learningModules = [
  {
    slug: 'folk-lore',
    title: 'Folk Lore Stories',
    description:
      'Traditional folk stories teaching values like patience, community, forgiveness, balance with nature, and wisdom.',
    difficulty: 'Beginner',
    xp_reward: 100,
    category: 'Folklore',
    estimated_time: '45 mins',
    hero_story:
      'A collection of traditional village stories passed through generations to teach wisdom, patience, kindness, and harmony with nature.',
  },
  {
    slug: 'herbal-wisdom',
    title: 'Herbal Wisdom',
    description:
      'Traditional herbal healing stories exploring the connection between nature, medicine, and human well-being.',
    difficulty: 'Intermediate',
    xp_reward: 120,
    category: 'Herbal Medicine',
    estimated_time: '50 mins',
    hero_story:
      'Stories about traditional healers, medicinal plants, and the balance between science and nature.',
  },
  {
    slug: 'traditional-farming',
    title: 'Traditional Farming',
    description:
      'Stories about sustainable agriculture, ancestral seeds, soil health, and harmony with the land.',
    difficulty: 'Intermediate',
    xp_reward: 130,
    category: 'Traditional Farming',
    estimated_time: '60 mins',
    hero_story:
      'Ancient farming wisdom teaching sustainability, patience, biodiversity, and respect for the earth.',
  },
] as const
