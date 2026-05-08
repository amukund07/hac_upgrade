import { AchievementModel } from '../models/Achievement'
import { LearningModuleModel } from '../models/LearningModule'
import { LessonModel } from '../models/Lesson'
import { QuizModel } from '../models/Quiz'
import { QuizQuestionModel } from '../models/QuizQuestion'
import { seedAchievements, seedLessons, seedModules, seedQuizQuestions, seedQuizzes, seedUsers } from './seedData'
import { seedUsersFromArray } from './authService'

const slugToModuleId = new Map<string, string>()
const titleToQuizId = new Map<string, string>()

export const seedDatabase = async () => {
  const modulesCount = await LearningModuleModel.countDocuments()

  if (modulesCount === 0) {
    for (const moduleSeed of seedModules) {
      const module = await LearningModuleModel.create(moduleSeed)
      slugToModuleId.set(moduleSeed.slug, String(module._id))
    }

    for (const lessonSeed of seedLessons) {
      const moduleId = slugToModuleId.get(lessonSeed.moduleSlug)

      if (!moduleId) {
        continue
      }

      await LessonModel.create({
        module_id: moduleId,
        slug: `${lessonSeed.moduleSlug}-${lessonSeed.order_index}`,
        title: lessonSeed.title,
        content: lessonSeed.content,
        order_index: lessonSeed.order_index,
      })
    }

    for (const quizSeed of seedQuizzes) {
      const moduleId = slugToModuleId.get(quizSeed.moduleSlug)

      if (!moduleId) {
        continue
      }

      const quiz = await QuizModel.create({
        module_id: moduleId,
        slug: `${quizSeed.moduleSlug}-quiz`,
        title: quizSeed.title,
        passing_score: quizSeed.passing_score,
      })

      titleToQuizId.set(quizSeed.title, String(quiz._id))
    }

    for (const questionSeed of seedQuizQuestions) {
      const quizId = titleToQuizId.get(questionSeed.quizTitle)

      if (!quizId) {
        continue
      }

      await QuizQuestionModel.create({
        quiz_id: quizId,
        question: questionSeed.question,
        options: questionSeed.options,
        correct_answer: questionSeed.correct_answer,
        order_index: questionSeed.order_index,
      })
    }

    for (const achievementSeed of seedAchievements) {
      await AchievementModel.create(achievementSeed)
    }
  }

  await seedUsersFromArray(seedUsers)
}