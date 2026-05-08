import { Schema, model, type InferSchemaType } from 'mongoose'

const learningModuleSchema = new Schema(
  {
    slug: { type: String, required: true, unique: true, trim: true },
    title: { type: String, required: true, trim: true },
    description: { type: String, required: true },
    difficulty: { type: String, required: true },
    xp_reward: { type: Number, required: true },
    category: { type: String, required: true },
    estimated_time: { type: String, required: true },
    hero_story: { type: String, default: '' },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    versionKey: false,
  },
)

export type LearningModuleDocument = InferSchemaType<typeof learningModuleSchema>
export const LearningModuleModel = model('LearningModule', learningModuleSchema)