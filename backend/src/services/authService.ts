import { Types } from 'mongoose'
import { UserModel } from '../models/User'
import { ApiError } from '../utils/errors'
import { calculateLevel } from '../utils/level'
import { generateToken } from '../utils/jwt'
import { comparePassword, hashPassword } from '../utils/password'
import { serializeDocument } from '../utils/serializers'

type RegisterInput = {
  name: string
  email: string
  password: string
}

type UpdateUserInput = {
  name?: string
  avatar_url?: string
  x_points?: number
  level?: number
  streak?: number
}

const stripPassword = (user: ReturnType<typeof serializeDocument>) => {
  if (!user) {
    return null
  }

  delete user.password_hash
  return user
}

export const registerUser = async ({ name, email, password }: RegisterInput) => {
  const existingUser = await UserModel.findOne({ email })

  if (existingUser) {
    throw new ApiError(409, 'A user with that email already exists')
  }

  const passwordHash = await hashPassword(password)
  // if client didn't provide a name, derive one from the email prefix
  const resolvedName = name?.trim() ? name.trim() : email.split('@')[0]
  const user = await UserModel.create({
    name: resolvedName,
    email,
    password_hash: passwordHash,
    xp_points: 0,
    level: 1,
    streak: 0,
    avatar_url: '',
  })

  const token = generateToken({ id: String(user._id), email: user.email })

  return {
    user: stripPassword(serializeDocument(user)),
    token,
  }
}

export const loginUser = async ({ email, password }: RegisterInput) => {
  const user = await UserModel.findOne({ email })

  if (!user) {
    throw new ApiError(401, 'Invalid email or password')
  }

  const isPasswordValid = await comparePassword(password, user.password_hash)

  if (!isPasswordValid) {
    throw new ApiError(401, 'Invalid email or password')
  }

  user.last_login_at = new Date()
  await user.save()

  const token = generateToken({ id: String(user._id), email: user.email })

  return {
    user: stripPassword(serializeDocument(user)),
    token,
  }
}

export const getCurrentUser = async (userId: string) => {
  const user = await UserModel.findById(userId)

  if (!user) {
    throw new ApiError(404, 'User not found')
  }

  return stripPassword(serializeDocument(user))
}

export const updateCurrentUser = async (userId: string, updates: UpdateUserInput) => {
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
  return stripPassword(serializeDocument(user))
}

export const incrementUserXP = async (userId: string, xpDelta: number) => {
  const user = await UserModel.findById(userId)

  if (!user) {
    throw new ApiError(404, 'User not found')
  }

  user.xp_points += xpDelta
  user.level = calculateLevel(user.xp_points)
  await user.save()

  return stripPassword(serializeDocument(user))
}

export const seedUsersFromArray = async (users: Array<{ name: string; email: string; password: string; avatar_url: string; xp_points: number; level: number; streak: number }>) => {
  for (const seedUser of users) {
    const existingUser = await UserModel.findOne({ email: seedUser.email })

    if (existingUser) {
      continue
    }

    const passwordHash = await hashPassword(seedUser.password)
    await UserModel.create({
      name: seedUser.name,
      email: seedUser.email,
      password_hash: passwordHash,
      avatar_url: seedUser.avatar_url,
      xp_points: seedUser.xp_points,
      level: seedUser.level,
      streak: seedUser.streak,
      last_login_at: new Date(),
      role: 'student',
      _id: new Types.ObjectId(),
    })
  }
}