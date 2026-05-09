import { GoogleGenAI } from '@google/genai'
import { env } from '../config/env'

export const generateChatResponse = async (question: string, contextSnippets: string[] = []) => {
  if (!env.geminiApiKey) {
    throw new Error('Gemini API key not configured')
  }

  const ai = new GoogleGenAI({ apiKey: env.geminiApiKey })
  
  const systemInstruction = `
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

  const contextText = contextSnippets.join("\n\n---\n\n");
  const prompt = `
    KNOWLEDGE BASE CONTEXT:
    ${contextText}

    USER QUERY:
    ${question}

    Help the user by applying this traditional wisdom to their modern life.
  `;

  const result = await ai.models.generateContent({
    model: 'gemini-1.5-flash',
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    systemInstruction: { parts: [{ text: systemInstruction }] }
  })

  // @ts-ignore
  return result.candidates?.[0]?.content?.parts?.[0]?.text ?? "The ancestors are silent today. Please try again later."
}
