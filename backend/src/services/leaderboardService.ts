import { UserModel } from '../models/User'
import { serializeCollection } from '../utils/serializers'

export const getLeaderboard = async () => {
  const users = await UserModel.find().sort({ xp_points: -1, level: -1 })
  return serializeCollection(users)
}