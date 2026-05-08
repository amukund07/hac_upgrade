import { ApiError } from '../utils/errors'

export const validateRegisterInput = (body: { name?: string; email?: string; password?: string }) => {
  // Name is optional; if omitted the server will derive a sensible default.
  if (!body.email?.trim()) {
    throw new ApiError(400, 'Email is required')
  }

  if (!body.password || body.password.length < 8) {
    throw new ApiError(400, 'Password must be at least 8 characters long')
  }
}

export const validateLoginInput = (body: { email?: string; password?: string }) => {
  if (!body.email?.trim()) {
    throw new ApiError(400, 'Email is required')
  }

  if (!body.password) {
    throw new ApiError(400, 'Password is required')
  }
}