import { Schema, model, type InferSchemaType } from 'mongoose'

const lessonSchema = new Schema(
  {
    module_id: { type: Schema.Types.ObjectId, ref: 'LearningModule', required: true },
    slug: { type: String, required: true, unique: true, trim: true },
    title: { type: String, required: true, trim: true },
    content: { type: String, required: true },
    order_index: { type: Number, default: 0 },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    versionKey: false,
  },
)

export type LessonDocument = InferSchemaType<typeof lessonSchema>
export const LessonModel = model('Lesson', lessonSchema)