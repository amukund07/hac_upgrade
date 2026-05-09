import { GoogleGenAI } from '@google/genai'
import { env } from '../config/env'

function getWavHeader(dataLength: number, sampleRate: number = 24000, channels: number = 1, bitsPerSample: number = 16) {
  const header = Buffer.alloc(44)
  header.write('RIFF', 0)
  header.writeUInt32LE(dataLength + 36, 4)
  header.write('WAVE', 8)
  header.write('fmt ', 12)
  header.writeUInt32LE(16, 16)
  header.writeUInt16LE(1, 20) // PCM
  header.writeUInt16LE(channels, 22)
  header.writeUInt32LE(sampleRate, 24)
  header.writeUInt32LE(sampleRate * channels * (bitsPerSample / 8), 28)
  header.writeUInt16LE(channels * (bitsPerSample / 8), 32)
  header.writeUInt16LE(bitsPerSample, 34)
  header.write('data', 36)
  header.writeUInt32LE(dataLength, 40)
  return header
}

export const synthesizeText = async (text: string) => {
  if (!env.geminiApiKey) {
    throw new Error('TTS provider not configured (GEMINI_API_KEY missing)')
  }

  const ai = new GoogleGenAI({ apiKey: env.geminiApiKey })

  const response = await ai.models.generateContent({
    model: 'gemini-3.1-flash-tts-preview',
    contents: [{ parts: [{ text }] }],
    config: {
      responseModalities: ['AUDIO'],
      speechConfig: {
        voiceConfig: {
          prebuiltVoiceConfig: { voiceName: 'Kore' },
        },
      },
    },
  })

  // @ts-ignore - response structure might vary slightly in preview SDK
  const data = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data

  if (!data) {
    throw new Error('Failed to generate audio content from Gemini')
  }

  const pcmBuffer = Buffer.from(data, 'base64')
  const wavHeader = getWavHeader(pcmBuffer.length)
  const fullWavBuffer = Buffer.concat([wavHeader, pcmBuffer])

  return fullWavBuffer.toString('base64')
}