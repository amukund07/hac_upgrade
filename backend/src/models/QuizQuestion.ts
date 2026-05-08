import { Schema, model, type InferSchemaType } from 'mongoose'

const quizQuestionSchema = new Schema(
  {
    quiz_id: { type: Schema.Types.ObjectId, ref: 'Quiz', required: true },
    question: { type: String, required: true },
    options: { type: [String], default: [] },
    correct_answer: { type: String, required: true },
    order_index: { type: Number, default: 0 },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    versionKey: false,
  },
)

export type QuizQuestionDocument = InferSchemaType<typeof quizQuestionSchema>
export const QuizQuestionModel = model('QuizQuestion', quizQuestionSchema)