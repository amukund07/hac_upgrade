import type { NextFunction, Request, Response } from 'express'
import jwt from 'jsonwebtoken'
import { env } from '../config/env'
import { ApiError } from '../utils/errors'

export type AuthenticatedRequest = Request & {
  user?: {
    id: string
    email: string
  }
}

export const protect = (req: AuthenticatedRequest, _res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization

  if (!authHeader?.startsWith('Bearer ')) {
    throw new ApiError(401, 'Not authorized, token missing')
  }

  const token = authHeader.split(' ')[1]
  const decoded = jwt.verify(token, env.jwtSecret) as { id: string; email: string }
  req.user = decoded
  next()
}