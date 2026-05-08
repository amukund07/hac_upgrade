import { Schema, model, type InferSchemaType } from 'mongoose'

const quizSchema = new Schema(
  {
    module_id: { type: Schema.Types.ObjectId, ref: 'LearningModule', required: true },
    slug: { type: String, required: true, unique: true, trim: true },
    title: { type: String, required: true, trim: true },
    passing_score: { type: Number, default: 70 },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    versionKey: false,
  },
)

export type QuizDocument = InferSchemaType<typeof quizSchema>
export const QuizModel = model('Quiz', quizSchema)