import 'dotenv/config'
import { connectDatabase, disconnectDatabase } from '../src/config/db'
import { LearningModuleModel } from '../src/models/LearningModule'
import { LessonModel } from '../src/models/Lesson'
import { QuizModel } from '../src/models/Quiz'
import { QuizQuestionModel } from '../src/models/QuizQuestion'
import { learningModules } from './seeds/learningModules.seed'
import { lessons } from './seeds/lessons.seed'
import { quizzes } from './seeds/quizzes.seed'
import { quizQuestions } from './seeds/quizQuestions.seed'

const seedLearningModules = async () => {
  const moduleIdBySlug = new Map<string, string>()

  for (const moduleSeed of learningModules) {
    const moduleDoc = await LearningModuleModel.findOneAndUpdate(
      { slug: moduleSeed.slug },
      {
        $set: {
          title: moduleSeed.title,
          description: moduleSeed.description,
          difficulty: moduleSeed.difficulty,
          xp_reward: moduleSeed.xp_reward,
          category: moduleSeed.category,
          estimated_time: moduleSeed.estimated_time,
          hero_story: moduleSeed.hero_story,
        },
        $setOnInsert: { slug: moduleSeed.slug },
      },
      { upsert: true, new: true },
    )

    if (moduleDoc) {
      moduleIdBySlug.set(moduleSeed.slug, String(moduleDoc._id))
    }
  }

  return moduleIdBySlug
}

const seedLessons = async (moduleIdBySlug: Map<string, string>) => {
  for (const lessonSeed of lessons) {
    const moduleId = moduleIdBySlug.get(lessonSeed.module_slug)

    if (!moduleId) {
      throw new Error(`Missing module for lesson: ${lessonSeed.slug}`)
    }

    await LessonModel.findOneAndUpdate(
      { slug: lessonSeed.slug },
      {
        $set: {
          module_id: moduleId,
          title: lessonSeed.title,
          content: lessonSeed.content.trim(),
          order_index: lessonSeed.order_index,
        },
        $setOnInsert: { slug: lessonSeed.slug },
      },
      { upsert: true, new: true },
    )
  }
}

const seedQuizzes = async (moduleIdBySlug: Map<string, string>) => {
  const quizIdBySlug = new Map<string, string>()

  for (const quizSeed of quizzes) {
    const moduleId = moduleIdBySlug.get(quizSeed.module_slug)

    if (!moduleId) {
      throw new Error(`Missing module for quiz: ${quizSeed.slug}`)
    }

    const quizDoc = await QuizModel.findOneAndUpdate(
      { slug: quizSeed.slug },
      {
        $set: {
          module_id: moduleId,
          title: quizSeed.title,
          passing_score: quizSeed.passing_score,
        },
        $setOnInsert: { slug: quizSeed.slug },
      },
      { upsert: true, new: true },
    )

    if (quizDoc) {
      quizIdBySlug.set(quizSeed.slug, String(quizDoc._id))
    }
  }

  return quizIdBySlug
}

const seedQuizQuestions = async (quizIdBySlug: Map<string, string>) => {
  for (const questionSeed of quizQuestions) {
    const quizId = quizIdBySlug.get(questionSeed.quiz_slug)

    if (!quizId) {
      throw new Error(`Missing quiz for question: ${questionSeed.question}`)
    }

    await QuizQuestionModel.findOneAndUpdate(
      { quiz_id: quizId, question: questionSeed.question },
      {
        $set: {
          options: questionSeed.options,
          correct_answer: questionSeed.correct_answer,
          order_index: questionSeed.order_index,
        },
        $setOnInsert: {
          quiz_id: quizId,
          question: questionSeed.question,
        },
      },
      { upsert: true, new: true },
    )
  }
}

const seed = async () => {
  await connectDatabase()

  try {
    const moduleIdBySlug = await seedLearningModules()
    await seedLessons(moduleIdBySlug)
    const quizIdBySlug = await seedQuizzes(moduleIdBySlug)
    await seedQuizQuestions(quizIdBySlug)

    console.log('Seed data inserted/updated successfully')
  } finally {
    await disconnectDatabase()
  }
}

seed().catch((error) => {
  console.error('Seeding error:', error)
  process.exit(1)
})
