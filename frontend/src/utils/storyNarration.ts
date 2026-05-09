export interface NarrationChunk {
  id: string
  paragraphIndex: number
  text: string
  tone: 'intro' | 'story' | 'wisdom'
}

const normalizeWhitespace = (text: string) => text.replace(/\r\n/g, '\n').replace(/[ \t]+/g, ' ').trim()

const addStrategicPauses = (text: string) => {
  let output = text

  output = output.replace(/\bbeta\b/gi, 'beta...')
  output = output.replace(/\b(moral|lesson|wisdom|remember this|always remember)\b[:\-]?/gi, '$1...')
  output = output.replace(/,\s+/g, ', ')
  output = output.replace(/([.!?])\s+/g, '$1 ')

  if (/\b(moral|lesson|wisdom|remember)\b/i.test(output)) {
    output = `... ${output} ...`
  }

  return output
}

const splitIntoSentences = (text: string) => {
  const sentences = text.match(/[^.!?]+[.!?]?/g) ?? [text]
  return sentences.map((sentence) => sentence.trim()).filter(Boolean)
}

const chunkSentences = (sentences: string[], maxLength: number) => {
  const chunks: string[] = []
  let current = ''

  sentences.forEach((sentence) => {
    if (!current) {
      current = sentence
      return
    }

    if ((current + ' ' + sentence).length > maxLength) {
      chunks.push(current.trim())
      current = sentence
      return
    }

    current = `${current} ${sentence}`
  })

  if (current.trim()) {
    chunks.push(current.trim())
  }

  return chunks
}

export const preprocessNarrationText = (text: string) => addStrategicPauses(normalizeWhitespace(text))

export const splitNarrationIntoChunks = (title: string, content: string, maxLength = 260): NarrationChunk[] => {
  const intro = preprocessNarrationText(
    `Now, beta... settle in softly. Let us walk through ${title} like a story told by a grandmother under the warm village lamp.`
  )

  const cleanedContent = normalizeWhitespace(content)
  const paragraphs = cleanedContent
    .split(/\n{2,}/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean)

  const chunks: NarrationChunk[] = [
    {
      id: 'intro',
      paragraphIndex: 0,
      text: intro,
      tone: 'intro',
    },
  ]

  if (!paragraphs.length) {
    return chunks
  }

  paragraphs.forEach((paragraph, paragraphIndex) => {
    const processedParagraph = preprocessNarrationText(paragraph)
    const isWisdomLine = /\b(moral|remember|wisdom|lesson|important|always)\b/i.test(processedParagraph)
    const chunkTexts = chunkSentences(splitIntoSentences(processedParagraph), maxLength)

    chunkTexts.forEach((chunkText, chunkIndex) => {
      chunks.push({
        id: `paragraph-${paragraphIndex}-${chunkIndex}`,
        paragraphIndex: paragraphIndex + 1,
        text: isWisdomLine ? `... ${chunkText} ...` : chunkText,
        tone: isWisdomLine ? 'wisdom' : 'story',
      })
    })
  })

  return chunks
}

export const buildNarrationPrompt = (chunk: NarrationChunk) => {
  const emotionHint = chunk.tone === 'wisdom'
    ? 'Speak with a slower, reflective pause and a gentle wise tone.'
    : chunk.tone === 'intro'
      ? 'Open softly and warmly, as if settling a child into the story.'
      : 'Keep the pacing calm, intimate, and emotionally grounded.'

  return `${emotionHint}\n\nNarration to speak:\n${chunk.text}`
}