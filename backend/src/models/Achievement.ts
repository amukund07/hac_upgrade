import { Schema, model, type InferSchemaType } from 'mongoose'

const achievementSchema = new Schema(
  {
    slug: { type: String, required: true, unique: true, trim: true },
    title: { type: String, required: true, trim: true },
    description: { type: String, required: true },
    xp_reward: { type: Number, default: 0 },
    icon: { type: String, default: '' },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    versionKey: false,
  },
)

export type AchievementDocument = InferSchemaType<typeof achievementSchema>
export const AchievementModel = model('Achievement', achievementSchema)