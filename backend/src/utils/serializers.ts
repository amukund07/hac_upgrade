export const serializeDocument = <T extends { _id?: unknown; __v?: unknown; toObject?: () => Record<string, unknown> }>(document: T | null) => {
  if (!document) {
    return null
  }

  const plain = typeof document.toObject === 'function' ? document.toObject() : { ...(document as Record<string, unknown>) }

  if (plain._id != null) {
    plain.id = String(plain._id)
    delete plain._id
  }

  delete plain.__v
  return plain
}

export const serializeCollection = <T extends { _id?: unknown; __v?: unknown; toObject?: () => Record<string, unknown> }>(documents: T[]) =>
  documents.map((document) => serializeDocument(document))