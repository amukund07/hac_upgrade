import { GoogleGenAI } from '@google/genai'
import { env } from '../config/env'

export const generateGeminiResponse = async (
  type: 'chat' | 'narration' | 'rag',
  payload: { question?: string; contextSnippets?: string[]; title?: string; content?: string }
) => {
  if (!env.geminiApiKey) {
    throw new Error('Gemini API key not configured')
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

  const result = await ai.models.generateContent({
    model: 'gemini-2.0-flash',
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    systemInstruction: { parts: [{ text: systemInstruction }] }
  })

  // @ts-ignore
  return result.candidates?.[0]?.content?.parts?.[0]?.text ?? "The ancestors are silent today."
}
