import { UserModel } from '../models/User'
import { ApiError } from '../utils/errors'
import { calculateLevel } from '../utils/level'
import { serializeDocument } from '../utils/serializers'

export const getUserProfile = async (userId: string) => {
  const user = await UserModel.findById(userId)

  if (!user) {
    throw new ApiError(404, 'User not found')
  }

  return serializeDocument(user)
}

export const updateXP = async (userId: string, xpDelta: number) => {
  const user = await UserModel.findById(userId)

  if (!user) {
    throw new ApiError(404, 'User not found')
  }

  user.xp_points += xpDelta
  user.level = calculateLevel(user.xp_points)
  await user.save()

  return serializeDocument(user)
}

export const updateUserProfile = async (userId: string, updates: { name?: string; avatar_url?: string; x_points?: number; level?: number; streak?: number }) => {
  const user = await UserModel.findById(userId)

  if (!user) {
    throw new ApiError(404, 'User not found')
  }

  if (typeof updates.name === 'string') {
    user.name = updates.name
  }

  if (typeof updates.avatar_url === 'string') {
    user.avatar_url = updates.avatar_url
  }

  if (typeof updates.x_points === 'number') {
    user.xp_points = updates.x_points
    user.level = calculateLevel(updates.x_points)
  }

  if (typeof updates.level === 'number') {
    user.level = updates.level
  }

  if (typeof updates.streak === 'number') {
    user.streak = updates.streak
  }

  await user.save()
  return serializeDocument(user)
}