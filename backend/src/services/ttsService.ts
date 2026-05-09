import axios from 'axios'
import { env } from '../config/env'

type TtsStyle = 'story' | 'lesson' | 'chat'

interface SynthesizeTextOptions {
  style?: TtsStyle
}

// Multiple models to try in order (fallback strategy)
const TTS_MODELS = [
  'gemini-2.0-flash',
  'gemini-1.5-flash',
  'gemini-1.5-flash-8b',
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

      const response = await axios.post(
        `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${env.geminiApiKey}`,
        {
          contents: [
            {
              role: 'user',
              parts: [{ text: prompt }],
            },
          ],
          generationConfig: {
            responseModalities: ['AUDIO'],
            speechConfig: {
              voiceConfig: {
                prebuiltVoiceConfig: { voiceName },
              },
            },
          },
        }
      )

      console.log(`[TTS] Response received from model ${model}:`, JSON.stringify(response.data, null, 2).substring(0, 500))

      // Extract audio data from response
      const data = response.data.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data

      console.log(`[TTS] Extracted audio data length: ${data ? data.length : 'null'}`)

      if (!data) {
        console.error(`[TTS] No audio data returned from model ${model}`)
        throw new Error(`No audio data returned from model ${model}`)
      }

      console.log(`[TTS] ✓ Successfully generated audio with model: ${model}, size: ${data.length} chars`)
      // Return audio with MIME type indicator for frontend
      return `data:audio/mp3;base64,${data}`
    } catch (error) {
      // Handle axios errors specifically
      if (axios.isAxiosError(error)) {
        const errorMsg = error.response?.data?.error?.message || error.message
        const errorCode = error.response?.status
        console.warn(`[TTS] Axios error with model ${model}: Status ${errorCode}, Message: ${errorMsg}`)
        console.warn(`[TTS] Error response:`, JSON.stringify(error.response?.data, null, 2).substring(0, 500))
        lastError = new Error(`${errorCode} - ${errorMsg}`)
      } else {
        lastError = error as Error
        const errorMsg = error instanceof Error ? error.message : String(error)
        console.warn(`[TTS] Failed with model ${model}: ${errorMsg}`)
        if (error instanceof Error) {
          console.warn(`[TTS] Error stack:`, error.stack)
        }
      }

      const errorMsg = lastError.message
      // Check if it's a rate limit or quota error
      if (
        errorMsg.includes('RESOURCE_EXHAUSTED') ||
        errorMsg.includes('QUOTA_EXCEEDED') ||
        errorMsg.includes('429') ||
        errorMsg.includes('500') ||
        errorMsg.includes('403')
      ) {
        console.log(`[TTS] Rate limit/quota/permission hit with ${model}, trying next model...`)
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

/**
 * Generate mock WAV audio data (minimal but valid)
 * Returns a base64-encoded WAV file with silence
 */
const generateMockAudio = (durationMs: number = 3000): string => {
  // Simple WAV header for silence
  // 44100 Hz, mono, 16-bit
  const sampleRate = 44100
  const numSamples = Math.floor((durationMs / 1000) * sampleRate)
  const audioData = new Float32Array(numSamples)

  // Fill with silence (zeros)
  audioData.fill(0)

  // Encode as WAV
  const wavBuffer = encodeWAV(audioData, sampleRate)
  const wavBase64 = Buffer.from(wavBuffer).toString('base64')

  return `data:audio/wav;base64,${wavBase64}`
}

/**
 * Encode PCM audio data to WAV format
 */
const encodeWAV = (samples: Float32Array, sampleRate: number): ArrayBuffer => {
  const frameLength = samples.length
  const numberOfChannels = 1
  const sampleWidth = 2
  const bytesPerSample = sampleWidth * numberOfChannels

  const arrayBuffer = new ArrayBuffer(44 + frameLength * bytesPerSample)
  const view = new DataView(arrayBuffer)
  const isLittleEndian = true

  // WAV header
  const writeString = (offset: number, string: string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i))
    }
  }

  // "RIFF" chunk descriptor
  writeString(0, 'RIFF')
  view.setUint32(4, 36 + frameLength * bytesPerSample, isLittleEndian)
  writeString(8, 'WAVE')

  // "fmt " sub-chunk
  writeString(12, 'fmt ')
  view.setUint32(16, 16, isLittleEndian) // subchunk1 size
  view.setUint16(20, 1, isLittleEndian) // PCM
  view.setUint16(22, numberOfChannels, isLittleEndian)
  view.setUint32(24, sampleRate, isLittleEndian)
  view.setUint32(28, sampleRate * bytesPerSample, isLittleEndian)
  view.setUint16(32, bytesPerSample, isLittleEndian)
  view.setUint16(34, 16, isLittleEndian) // bits per sample

  // "data" sub-chunk
  writeString(36, 'data')
  view.setUint32(40, frameLength * bytesPerSample, isLittleEndian)

  // Write samples
  let offset = 44
  for (let i = 0; i < frameLength; i++) {
    view.setInt16(offset, samples[i] < 0 ? samples[i] * 0x8000 : samples[i] * 0x7fff, isLittleEndian)
    offset += 2
  }

  return arrayBuffer
}

export const synthesizeText = async (text: string, options: SynthesizeTextOptions = {}): Promise<string> => {
  if (!env.geminiApiKey) {
    console.warn('[TTS] Gemini API key not configured, using mock audio')
    // Return mock audio so testing can continue
    return generateMockAudio(Math.min(text.length * 50, 8000)) // Estimate duration
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
    const style = options.style ?? 'story'

    console.log(`[TTS] Starting synthesis for style: ${style}, text length: ${text.length}`)

    const audioData = await tryModelWithFallback(text, style, TTS_MODELS)

    console.log(`[TTS] Successfully generated audio data (${audioData.length} chars)`)
    return audioData
  } catch (error) {
    console.error('[TTS] Synthesis failed:', error)
    throw new Error(`Text-to-speech conversion failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}