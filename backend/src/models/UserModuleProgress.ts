import { Schema, model, type InferSchemaType } from 'mongoose'

const userModuleProgressSchema = new Schema(
  {
    user_id: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    module_id: { type: Schema.Types.ObjectId, ref: 'LearningModule', required: true },
    progress_percentage: { type: Number, default: 0 },
    completed_lessons_count: { type: Number, default: 0 },
    total_lessons_count: { type: Number, default: 0 },
    completed_at: { type: Date, default: null },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    versionKey: false,
  },
)

userModuleProgressSchema.index({ user_id: 1, module_id: 1 }, { unique: true })

export type UserModuleProgressDocument = InferSchemaType<typeof userModuleProgressSchema>
export const UserModuleProgressModel = model('UserModuleProgress', userModuleProgressSchema)