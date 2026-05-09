import asyncHandler from 'express-async-handler'
import type { Request, Response } from 'express'
import { sendResponse } from '../utils/response'
import { synthesizeText } from '../services/ttsService'

export const synthesize = asyncHandler(async (req: Request, res: Response) => {
  const { text, style } = req.body

  if (!text || typeof text !== 'string') {
    void sendResponse({ res, statusCode: 400, message: 'Missing text in request body' })
    return
  }

  try {
    const audioData = await synthesizeText(text, {
      style: style === 'lesson' || style === 'chat' ? style : 'story',
    })

    console.log(`[Controller] TTS synthesis successful, audio data length: ${audioData.length}`)

    void sendResponse({
      res,
      statusCode: 200,
      message: 'Narration generated successfully.',
      data: { 
        audioBase64: audioData, 
        fallback: 'gemini',
        format: audioData.startsWith('data:audio/mp3') ? 'mp3' : 'wav'
      },
    })
  } catch (error) {
    console.error('[Controller] TTS synthesis failed:', error)
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    void sendResponse({
      res,
      statusCode: 500,
      message: `Text-to-speech failed: ${errorMessage}`,
    })
  }
})
