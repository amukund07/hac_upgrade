import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import { getLessonsByModuleId, getModuleById, getModules, getQuizzesByModuleId, getQuizByModuleId } from '../services/moduleService'
import { sendResponse } from '../utils/response'

export const listModules = asyncHandler(async (_req: Request, res: Response) => {
  const modules = await getModules()
  void sendResponse({ res, statusCode: 200, data: modules })
})

export const fetchModule = asyncHandler(async (req: Request, res: Response) => {
  const module = await getModuleById(String(req.params.id))
  void sendResponse({ res, statusCode: 200, data: module })
})

export const moduleLessons = asyncHandler(async (req: Request, res: Response) => {
  const lessons = await getLessonsByModuleId(String(req.params.moduleId))
  void sendResponse({ res, statusCode: 200, data: lessons })
})

export const moduleQuizzes = asyncHandler(async (req: Request, res: Response) => {
  const quizzes = await getQuizzesByModuleId(String(req.params.moduleId))
  void sendResponse({ res, statusCode: 200, data: quizzes })
})

export const moduleQuiz = asyncHandler(async (req: Request, res: Response) => {
  const quiz = await getQuizByModuleId(String(req.params.moduleId))
  void sendResponse({ res, statusCode: 200, data: quiz })
})