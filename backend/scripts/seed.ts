import 'dotenv/config'
import { connectDatabase, disconnectDatabase } from '../src/config/db'
import { LearningModuleModel } from '../src/models/LearningModule'
import { LessonModel } from '../src/models/Lesson'
import { QuizModel } from '../src/models/Quiz'
import { QuizQuestionModel } from '../src/models/QuizQuestion'

const seed = async () => {
  await connectDatabase()

  const modules = [
    {
      slug: 'ayurveda-basics',
      title: 'Ayurveda Basics',
      description: 'Introduction to Ayurveda: doshas, daily routines, and basic herbs.',
      difficulty: 'Beginner',
      xp_reward: 100,
      category: 'Ayurveda',
      estimated_time: '15m',
    },
    {
      slug: 'sustainable-farming',
      title: 'Sustainable Farming',
      description: 'Traditional sustainable farming practices and companion planting.',
      difficulty: 'Intermediate',
      xp_reward: 150,
      category: 'Farming',
      estimated_time: '25m',
    },
    {
      slug: 'vedic-mathematics',
      title: 'Vedic Mathematics',
      description: 'Shortcuts and patterns for fast mental calculation from Vedic tradition.',
      difficulty: 'Beginner',
      xp_reward: 120,
      category: 'Mathematics',
      estimated_time: '20m',
    },
  ]

  for (const mod of modules) {
    const existing = await LearningModuleModel.findOne({ slug: mod.slug })
    if (!existing) {
      await LearningModuleModel.create(mod)
      console.log('Inserted module', mod.slug)
    }
  }

  const ayurveda = await LearningModuleModel.findOne({ slug: 'ayurveda-basics' })
  if (ayurveda) {
    const lessons = [
      {
        module_id: ayurveda._id,
        slug: 'dosha-intro',
        title: 'Understanding the Doshas',
        content: 'Vata, Pitta, and Kapha are the three doshas... (lesson content)'.repeat(5),
        order_index: 0,
      },
      {
        module_id: ayurveda._id,
        slug: 'daily-routine',
        title: 'Daily Routine (Dinacharya)',
        content: 'A simple daily routine supports balance... (lesson content)'.repeat(5),
        order_index: 1,
      },
    ]

    for (const ls of lessons) {
      const existing = await LessonModel.findOne({ slug: ls.slug })
      if (!existing) {
        await LessonModel.create(ls)
        console.log('Inserted lesson', ls.slug)
      }
    }

    const quiz = await QuizModel.findOne({ slug: 'ayurveda-quiz' })
    if (!quiz) {
      const created = await QuizModel.create({ module_id: ayurveda._id, slug: 'ayurveda-quiz', title: 'Ayurveda Basics Quiz', passing_score: 70 })
      await QuizQuestionModel.create({ quiz_id: created._id, question: 'Which dosha is associated with movement?', options: ['Vata', 'Pitta', 'Kapha'], correct_answer: 'Vata', order_index: 0 })
      await QuizQuestionModel.create({ quiz_id: created._id, question: 'Which practice is part of dinacharya?', options: ['Oil pulling', 'Running a marathon', 'Skydiving'], correct_answer: 'Oil pulling', order_index: 1 })
      console.log('Inserted quiz ayurveda-quiz')
    }
  }

  // Add similar seeding for other modules if desired (sustainable-farming, vedic-mathematics)

  await disconnectDatabase()
  console.log('Seeding complete')
}

seed().catch((err) => {
  console.error('Seeding error', err)
  process.exit(1)
})
