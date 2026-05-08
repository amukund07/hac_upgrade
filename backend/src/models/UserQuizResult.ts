import { Schema, model, type InferSchemaType } from 'mongoose'

const userQuizResultSchema = new Schema(
  {
    user_id: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    quiz_id: { type: Schema.Types.ObjectId, ref: 'Quiz', required: true },
    score: { type: Number, required: true },
    total_questions: { type: Number, required: true },
    passed: { type: Boolean, required: true },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    versionKey: false,
  },
)

export type UserQuizResultDocument = InferSchemaType<typeof userQuizResultSchema>
export const UserQuizResultModel = model('UserQuizResult', userQuizResultSchema)