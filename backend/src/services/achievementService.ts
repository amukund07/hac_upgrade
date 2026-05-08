import { AchievementModel } from '../models/Achievement'
import { UserAchievementModel } from '../models/UserAchievement'
import { serializeCollection, serializeDocument } from '../utils/serializers'

export const getAchievements = async () => {
  const achievements = await AchievementModel.find().sort({ created_at: -1 })
  return serializeCollection(achievements)
}

export const unlockAchievement = async (payload: {
  user_id: string
  achievement_id: string
  unlocked_at: Date
}) => {
  const userAchievement = await UserAchievementModel.findOneAndUpdate(
    { user_id: payload.user_id, achievement_id: payload.achievement_id },
    {
      unlocked_at: payload.unlocked_at,
    },
    { upsert: true, new: true },
  )

  return serializeDocument(userAchievement)
}

export const getUserAchievements = async (userId: string) => {
  const achievements = await UserAchievementModel.find({ user_id: userId }).populate('achievement_id')
  return serializeCollection(achievements)
}