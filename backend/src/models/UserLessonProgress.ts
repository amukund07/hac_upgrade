import { Schema, model, type InferSchemaType } from 'mongoose'

const userLessonProgressSchema = new Schema(
  {
    user_id: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    lesson_id: { type: Schema.Types.ObjectId, ref: 'Lesson', required: true },
    completed: { type: Boolean, default: false },
    completed_at: { type: Date, default: null },
    progress_percentage: { type: Number, default: 0 },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    versionKey: false,
  },
)

userLessonProgressSchema.index({ user_id: 1, lesson_id: 1 }, { unique: true })

export type UserLessonProgressDocument = InferSchemaType<typeof userLessonProgressSchema>
export const UserLessonProgressModel = model('UserLessonProgress', userLessonProgressSchema)