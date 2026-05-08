import { env } from '../config/env'

export const synthesizeText = async (text: string) => {
  if (!env.geminiApiKey) {
    throw new Error('TTS provider not configured (GEMINI_API_KEY missing)')
  }

  const url = new URL('https://texttospeech.googleapis.com/v1/text:synthesize')
  url.searchParams.set('key', env.geminiApiKey)

  const body = {
    input: { text },
    voice: { languageCode: 'en-US', name: 'en-US-Wavenet-D' },
    audioConfig: { audioEncoding: 'MP3' },
  }

  const response = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const responseText = await response.text()
    throw new Error(`TTS provider error: ${response.status} ${responseText}`)
  }

  const data = await response.json()

  return data.audioContent as string
}