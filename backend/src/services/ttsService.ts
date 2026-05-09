import { GoogleGenAI } from '@google/genai'
import { env } from '../config/env'

type TtsStyle = 'story' | 'lesson' | 'chat'

interface SynthesizeTextOptions {
  style?: TtsStyle
}

// Multiple models to try in order (fallback strategy)
const TTS_MODELS = [
  'gemini-3.1-flash-tts-preview',
  'gemini-2.0-flash-exp',
  'gemini-1.5-pro-exp-20250514',
]

const getVoiceConfig = (style: TtsStyle) => {
  switch (style) {
    case 'story':
      return 'Kore' // Warm, narrative voice for stories
    case 'lesson':
      return 'Kore' // Clear, educational voice
    case 'chat':
      return 'Kore' // Conversational voice
    default:
      return 'Kore'
  }
}

const buildSpeechPrompt = (text: string, style: TtsStyle) => {
  const narrationStyle =
    style === 'story'
      ? 'You are an elderly Indian grandmother telling a traditional bedtime folk story to a child in a calm peaceful village night. Speak slowly, warmly, emotionally, and naturally. Use soft pauses. Sound reflective and wise. Emphasize emotional moments gently. Never sound robotic, corporate, or like a voice assistant. Narration should feel intimate, comforting, and human.'
      : style === 'chat'
        ? 'You are a calm, thoughtful assistant speaking in a warm, human, and reassuring tone. Keep your pacing natural and avoid sounding mechanical.'
        : 'You are a gentle, wise storyteller narrating a lesson in a warm, calm, and engaging tone. Use natural pauses and a human rhythm.'

  return `${narrationStyle}\n\n${text}`
}

const tryModelWithFallback = async (
  ai: InstanceType<typeof GoogleGenAI>,
  text: string,
  style: TtsStyle,
  modelsToTry: string[]
): Promise<string> => {
  let lastError: Error | null = null

  for (const model of modelsToTry) {
    try {
      console.log(`[TTS] Attempting synthesis with model: ${model}`)
      const voiceName = getVoiceConfig(style)
      const prompt = buildSpeechPrompt(text, style)

      const response = await ai.models.generateContent({
        model,
        contents: [{ parts: [{ text: prompt }] }],
        config: {
          responseModalities: ['AUDIO'],
          speechConfig: {
            voiceConfig: {
              prebuiltVoiceConfig: { voiceName },
            },
          },
        },
      })

      console.log(`[TTS] Response received from model ${model}:`, JSON.stringify(response, null, 2).substring(0, 500))

      // Extract audio data from response
      // @ts-ignore - response structure from preview SDK
      const data = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data

      console.log(`[TTS] Extracted audio data length: ${data ? data.length : 'null'}`)

      if (!data) {
        console.error(`[TTS] No audio data returned from model ${model}`)
        throw new Error(`No audio data returned from model ${model}`)
      }

      console.log(`[TTS] ✓ Successfully generated audio with model: ${model}, size: ${data.length} chars`)
      // Return audio with MIME type indicator for frontend
      // Gemini returns base64 audio data
      return `data:audio/mp3;base64,${data}`
    } catch (error) {
      lastError = error as Error
      const errorMsg = error instanceof Error ? error.message : String(error)
      console.warn(`[TTS] Failed with model ${model}: ${errorMsg}`)
      console.warn(`[TTS] Error stack:`, error instanceof Error ? error.stack : '')

      // Check if it's a rate limit or quota error
      if (
        errorMsg.includes('RESOURCE_EXHAUSTED') ||
        errorMsg.includes('QUOTA_EXCEEDED') ||
        errorMsg.includes('429') ||
        errorMsg.includes('500')
      ) {
        console.log(`[TTS] Rate limit/quota hit with ${model}, trying next model...`)
        continue // Try next model
      }

      // For other errors, still try next model
      continue
    }
  }

  // If all models failed, throw the last error
  throw new Error(
    `TTS failed with all models. Last error: ${lastError?.message || 'Unknown error'}. Models tried: ${modelsToTry.join(', ')}`
  )
}

export const synthesizeText = async (text: string, options: SynthesizeTextOptions = {}): Promise<string> => {
  if (!env.geminiApiKey) {
    throw new Error('TTS provider not configured (GEMINI_API_KEY missing)')
  }

  // Ensure text is not too long
  if (!text || text.length === 0) {
    throw new Error('Text cannot be empty')
  }

  if (text.length > 5000) {
    console.warn(`[TTS] Text is ${text.length} characters, truncating to 5000`)
    // Truncate to last complete sentence within 5000 chars
    const truncated = text.substring(0, 5000)
    const lastPeriod = truncated.lastIndexOf('.')
    return synthesizeText(lastPeriod > 0 ? truncated.substring(0, lastPeriod + 1) : truncated, options)
  }

  try {
    const ai = new GoogleGenAI({ apiKey: env.geminiApiKey })
    const style = options.style ?? 'story'

    console.log(`[TTS] Starting synthesis for style: ${style}, text length: ${text.length}`)

    const audioData = await tryModelWithFallback(ai, text, style, TTS_MODELS)

    console.log(`[TTS] Successfully generated audio data (${audioData.length} chars)`)
    return audioData
  } catch (error) {
    console.error('[TTS] Synthesis failed:', error)
    throw new Error(`Text-to-speech conversion failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}