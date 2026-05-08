import { UserModuleProgressModel } from '../models/UserModuleProgress'
import { UserLessonProgressModel } from '../models/UserLessonProgress'
import { LessonModel } from '../models/Lesson'
import { ApiError } from '../utils/errors'
import { serializeDocument } from '../utils/serializers'

export const getUserModuleProgress = async (userId: string, moduleId: string) => {
  const progress = await UserModuleProgressModel.findOne({ user_id: userId, module_id: moduleId })
  return serializeDocument(progress)
}

export const updateModuleProgress = async (payload: {
  user_id: string
  module_id: string
  progress_percentage: number
  completed_lessons_count?: number
  total_lessons_count?: number
  completed_at?: string | null
}) => {
  const progress = await UserModuleProgressModel.findOneAndUpdate(
    { user_id: payload.user_id, module_id: payload.module_id },
    {
      progress_percentage: payload.progress_percentage,
      completed_lessons_count: payload.completed_lessons_count ?? 0,
      total_lessons_count: payload.total_lessons_count ?? 0,
      completed_at: payload.completed_at ? new Date(payload.completed_at) : null,
    },
    { upsert: true, new: true },
  )

  return serializeDocument(progress)
}

export const getUserLessonProgress = async (userId: string, lessonId: string) => {
  const progress = await UserLessonProgressModel.findOne({ user_id: userId, lesson_id: lessonId })
  return serializeDocument(progress)
}

export const recalculateModuleProgress = async (userId: string, moduleId: string) => {
  const moduleLessons = await LessonModel.find({ module_id: moduleId }).select('_id')
  const moduleLessonIds = moduleLessons.map((moduleLesson) => moduleLesson._id)
  const totalLessonsCount = moduleLessonIds.length
  if (!totalLessonsCount) {
    throw new ApiError(404, 'Module lessons not found')
  }

  const completedLessonsCount = await UserLessonProgressModel.countDocuments({
    user_id: userId,
    lesson_id: { $in: moduleLessonIds },
    completed: true,
  })

  const progressPercentage = Math.round((completedLessonsCount / totalLessonsCount) * 100)

  return updateModuleProgress({
    user_id: userId,
    module_id: moduleId,
    progress_percentage: progressPercentage,
    completed_lessons_count: completedLessonsCount,
    total_lessons_count: totalLessonsCount,
    completed_at: progressPercentage === 100 ? new Date().toISOString() : null,
  })
}