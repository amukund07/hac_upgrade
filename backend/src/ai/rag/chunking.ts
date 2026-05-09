/**
 * Knowledge Chunking Utility
 * Splits long content into semantic chunks with overlap for RAG
 */

export interface Chunk {
  text: string
  chunkIndex: number
  startIndex: number
  endIndex: number
}

/**
 * Split text into chunks with configurable size and overlap
 * Tries to break at sentence boundaries for semantic coherence
 */
export const chunkText = (
  text: string,
  chunkSize: number = 500,
  overlapSize: number = 100
): Chunk[] => {
  if (!text || text.length === 0) {
    return []
  }

  const chunks: Chunk[] = []
  let startIndex = 0
  let chunkIndex = 0

  while (startIndex < text.length) {
    const endIndex = Math.min(startIndex + chunkSize, text.length)
    
    // Try to break at sentence boundary to avoid cutting mid-sentence
    let actualEndIndex = endIndex
    if (endIndex < text.length) {
      // Look backwards for sentence boundary (. ! ? or newline)
      const lookbackText = text.substring(Math.max(0, endIndex - 100), endIndex)
      const lastSentenceEnd = Math.max(
        lookbackText.lastIndexOf('.'),
        lookbackText.lastIndexOf('!'),
        lookbackText.lastIndexOf('?'),
        lookbackText.lastIndexOf('\n')
      )
      
      if (lastSentenceEnd > 50) { // Only if we found a boundary reasonably close
        actualEndIndex = Math.max(0, endIndex - 100) + lastSentenceEnd + 1
      }
    }

    const chunk = text.substring(startIndex, actualEndIndex).trim()
    
    if (chunk.length > 0) {
      chunks.push({
        text: chunk,
        chunkIndex,
        startIndex,
        endIndex: actualEndIndex,
      })
      chunkIndex++
    }

    // Move start position forward, accounting for overlap
    startIndex = Math.max(startIndex + chunkSize - overlapSize, actualEndIndex)
    
    if (actualEndIndex >= text.length) break
  }

  return chunks
}

/**
 * Process knowledge base entry into chunks
 * Concatenates relevant fields and chunks the combined text
 */
export const chunkKnowledgeEntry = (
  entry: Record<string, any>,
  options = { chunkSize: 500, overlapSize: 100 }
) => {
  // Build comprehensive text from various fields
  const textParts: string[] = []

  // Add title
  if (entry.title) {
    textParts.push(`Title: ${entry.title}`)
  }

  // Add summary if available
  if (entry.summary) {
    textParts.push(`Summary: ${entry.summary}`)
  }

  // Add domain and subdomain info
  if (entry.domain) {
    textParts.push(`Domain: ${entry.domain}`)
  }
  if (entry.subdomain) {
    textParts.push(`Subdomain: ${entry.subdomain}`)
  }

  // Add story/narrative content
  if (entry.dadi_story) {
    textParts.push(`Traditional Wisdom: ${entry.dadi_story}`)
  }

  // Add health benefits if it's a remedy
  if (entry.health_benefits && Array.isArray(entry.health_benefits)) {
    textParts.push(`Benefits: ${entry.health_benefits.join(', ')}`)
  }

  // Add remedy steps if available
  if (entry.remedy_steps && Array.isArray(entry.remedy_steps)) {
    textParts.push(`Steps:\n${entry.remedy_steps.join('\n')}`)
  }

  // Add ingredients if available
  if (entry.ingredients && Array.isArray(entry.ingredients)) {
    textParts.push(`Ingredients: ${entry.ingredients.join(', ')}`)
  }

  // Add scientific backing
  if (entry.scientific_backing && Array.isArray(entry.scientific_backing)) {
    textParts.push(`Scientific Evidence:\n${entry.scientific_backing.join('\n')}`)
  }

  // Add modern relevance
  if (entry.modern_relevance && Array.isArray(entry.modern_relevance)) {
    textParts.push(`Modern Relevance: ${entry.modern_relevance.join(', ')}`)
  }

  // Add keywords
  if (entry.keywords && Array.isArray(entry.keywords)) {
    textParts.push(`Keywords: ${entry.keywords.join(', ')}`)
  }

  // Add yoga poses if available
  if (entry.yoga_poses && Array.isArray(entry.yoga_poses) && entry.yoga_poses.length > 0) {
    textParts.push(`Yoga Poses: ${entry.yoga_poses.join(', ')}`)
  }

  // Combine all parts
  const fullText = textParts.join('\n\n')

  // Chunk the combined text
  return chunkText(fullText, options.chunkSize, options.overlapSize)
}

/**
 * Calculate optimal chunk size based on content type
 */
export const getOptimalChunkSize = (contentType?: string): number => {
  const sizeMap: Record<string, number> = {
    remedy: 400,
    story: 600,
    technique: 500,
    historical: 550,
    practice: 450,
    general: 500,
  }
  
  return sizeMap[contentType || 'general'] || 500
}
