import { env } from '../config/env'

export const synthesizeText = async (text: string) => {
  if (!env.geminiApiKey) {
    throw new Error('TTS provider not configured (GEMINI_API_KEY missing)')
  }

  // Using Google's Text-to-Speech REST endpoint as an example. The exact
  // Gemini/Google generative TTS endpoint may differ; update as needed.
  const url = 'https://texttospeech.googleapis.com/v1/text:synthesize'

  const body = {
    input: { text },
    voice: { languageCode: 'en-US', name: 'en-US-Wavenet-D' },
    audioConfig: { audioEncoding: 'MP3' },
  }

  const resp = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.geminiApiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })

  if (!resp.ok) {
    const txt = await resp.text()
    throw new Error(`TTS provider error: ${resp.status} ${txt}`)
  }

  const data = await resp.json()

  // `audioContent` is base64-encoded audio data
  return data.audioContent as string
}
