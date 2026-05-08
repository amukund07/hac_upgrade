import type { NextFunction, Request, Response } from 'express'
import { ApiError } from '../utils/errors'

export const notFound = (_req: Request, _res: Response, next: NextFunction) => {
  next(new ApiError(404, 'Route not found'))
}

export const errorHandler = (err: unknown, _req: Request, res: Response, _next: NextFunction) => {
  if (err instanceof ApiError) {
    return res.status(err.statusCode).json({ success: false, message: err.message })
  }

  const message = err instanceof Error ? err.message : 'Internal server error'
  return res.status(500).json({ success: false, message })
}