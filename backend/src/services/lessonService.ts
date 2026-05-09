import { LessonModel } from '../models/Lesson'
import { UserLessonProgressModel } from '../models/UserLessonProgress'
import { UserModuleProgressModel } from '../models/UserModuleProgress'
import { LearningModuleModel } from '../models/LearningModule'
import { ApiError } from '../utils/errors'
import { serializeDocument } from '../utils/serializers'
import { incrementUserXP } from './authService'

export const getLessonById = async (lessonId: string) => {
  const lesson = await LessonModel.findById(lessonId)

  if (!lesson) {
    throw new ApiError(404, 'Lesson not found')
  }

  return serializeDocument(lesson)
}

export const completeLesson = async (userId: string, lessonId: string) => {
  const lesson = await LessonModel.findById(lessonId)

  if (!lesson) {
    throw new ApiError(404, 'Lesson not found')
  }

  const progress = await UserLessonProgressModel.findOneAndUpdate(
    { user_id: userId, lesson_id: lessonId },
    {
      completed: true,
      completed_at: new Date(),
      progress_percentage: 100,
    },
    { upsert: true, new: true },
  )

  // Add XP for completing a lesson (e.g., 50 XP)
  await incrementUserXP(userId, 50)

  const module = await LearningModuleModel.findById(lesson.module_id)
  if (module) {
    const moduleLessons = await LessonModel.find({ module_id: lesson.module_id }).select('_id')
    const moduleLessonIds = moduleLessons.map((moduleLesson) => moduleLesson._id)

    const completedLessonsCount = await UserLessonProgressModel.countDocuments({
      user_id: userId,
      lesson_id: { $in: moduleLessonIds },
      completed: true,
    })

    const totalLessonsCount = await LessonModel.countDocuments({ module_id: lesson.module_id })
    const progressPercentage = totalLessonsCount > 0 ? Math.round((completedLessonsCount / totalLessonsCount) * 100) : 0

    await UserModuleProgressModel.findOneAndUpdate(
      { user_id: userId, module_id: lesson.module_id },
      {
        completed_lessons_count: completedLessonsCount,
        total_lessons_count: totalLessonsCount,
        progress_percentage: progressPercentage,
        completed_at: progressPercentage === 100 ? new Date() : null,
      },
      { upsert: true, new: true },
    )
  }

  return serializeDocument(progress)
}

export const getUserLessonProgress = async (userId: string, lessonId: string) => {
  const progress = await UserLessonProgressModel.findOne({ user_id: userId, lesson_id: lessonId })
  return serializeDocument(progress)
}