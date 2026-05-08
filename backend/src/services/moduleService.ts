import { LearningModuleModel } from '../models/LearningModule'
import { LessonModel } from '../models/Lesson'
import { QuizModel } from '../models/Quiz'
import { ApiError } from '../utils/errors'
import { serializeDocument, serializeCollection } from '../utils/serializers'

export const getModules = async () => {
  const modules = await LearningModuleModel.find().sort({ created_at: -1 })
  return serializeCollection(modules)
}

export const getModuleById = async (moduleId: string) => {
  const module = await LearningModuleModel.findById(moduleId)

  if (!module) {
    throw new ApiError(404, 'Module not found')
  }

  return serializeDocument(module)
}

export const getLessonsByModuleId = async (moduleId: string) => {
  const lessons = await LessonModel.find({ module_id: moduleId }).sort({ order_index: 1 })
  return serializeCollection(lessons)
}

export const getQuizzesByModuleId = async (moduleId: string) => {
  const quizzes = await QuizModel.find({ module_id: moduleId }).sort({ created_at: -1 })
  return serializeCollection(quizzes)
}

export const getQuizByModuleId = async (moduleId: string) => {
  const quiz = await QuizModel.findOne({ module_id: moduleId }).sort({ created_at: -1 })

  if (!quiz) {
    throw new ApiError(404, 'Quiz not found for module')
  }

  return serializeDocument(quiz)
}