import { Schema, model, type InferSchemaType } from 'mongoose'

const userAchievementSchema = new Schema(
  {
    user_id: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    achievement_id: { type: Schema.Types.ObjectId, ref: 'Achievement', required: true },
    unlocked_at: { type: Date, required: true },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    versionKey: false,
  },
)

userAchievementSchema.index({ user_id: 1, achievement_id: 1 }, { unique: true })

export type UserAchievementDocument = InferSchemaType<typeof userAchievementSchema>
export const UserAchievementModel = model('UserAchievement', userAchievementSchema)