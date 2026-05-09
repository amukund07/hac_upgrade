import { GoogleGenAI } from '@google/genai'
import { env } from '../config/env'

type GeminiRequestType = 'chat' | 'narration' | 'rag'

const fallbackResponseByType: Record<GeminiRequestType, string> = {
  chat: 'I can still help with traditional wisdom basics right now. Please try again in a moment for a richer AI response.',
  rag: 'I could not generate a full context-based answer right now. Please retry, or ask a narrower question so I can help step-by-step.',
  narration: 'Here is a simple narration: This lesson teaches traditional knowledge through lived experience, community practice, and respect for nature. Review the key ideas slowly and relate them to daily life.',
}

const getTextFromResult = (result: unknown): string | undefined => {
  if (!result || typeof result !== 'object') {
    return undefined
  }

  const maybeResult = result as {
    text?: string
    candidates?: Array<{
      content?: {
        parts?: Array<{ text?: string }>
      }
    }>
  }

  const directText = maybeResult.text?.trim()
  if (directText) {
    return directText
  }

  const candidateText = maybeResult.candidates?.[0]?.content?.parts?.[0]?.text?.trim()
  return candidateText || undefined
}

export const generateGeminiResponse = async (
  type: GeminiRequestType,
  payload: { question?: string; contextSnippets?: string[]; title?: string; content?: string }
) => {
  if (!env.geminiApiKey) {
    return fallbackResponseByType[type]
  }

  const ai = new GoogleGenAI({ apiKey: env.geminiApiKey })
  
  let systemInstruction = '';
  let prompt = '';

  if (type === 'chat' || type === 'rag') {
    systemInstruction = `
      You are the "Wisdom Guide," a bridge between ancient traditional knowledge and modern Gen-Z lifestyle.
      Your tone is:
      - Authentically cultural (like a wise elder or "Dadi").
      - Digitally savvy (understand modern trends and sustainability).
      - Practical and evidence-based (include scientific backing if provided).

      Rules:
      1. Use the provided context to answer. 
      2. If "dadi_story" is available, use its warm, storytelling tone.
      3. If "gen_z_hook" is available, use it to connect with younger audiences.
      4. Always highlight "modern_relevance" or "scientific_backing" to show why this tradition matters today.
      5. If the answer is not in the context, be honest but suggest related wisdom from the context.
    `
    const contextText = (payload.contextSnippets ?? []).join("\n\n---\n\n");
    prompt = `
      KNOWLEDGE BASE CONTEXT:
      ${contextText}

      USER QUERY:
      ${payload.question}

      Help the user by applying this traditional wisdom to their modern life.
    `;
  } else if (type === 'narration') {
    systemInstruction = `
      You turn lesson content into a warm, natural spoken narration.
      Keep the meaning intact, sound human, and avoid bullet points.
      Aim for 90 to 140 words.
    `;
    prompt = `
      Lesson title: ${payload.title}
      Lesson content: ${payload.content}

      Rewrite this as a smooth narration a learner can listen to while studying.
    `;
  }

  try {
    const result = await ai.models.generateContent({
      model: 'gemini-2.0-flash',
      contents: [{ role: 'user', parts: [{ text: `${systemInstruction}\n\n${prompt}` }] }],
    })

    return getTextFromResult(result) ?? fallbackResponseByType[type]
  } catch (error) {
    console.error('Gemini generation failed:', error)
    return fallbackResponseByType[type]
  }
}
