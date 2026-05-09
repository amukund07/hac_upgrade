import { useEffect, useRef, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:5000/api'

export const useLessonNarration = () => {
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel()
    }
  }, [])

  const stopNarration = () => {
    window.speechSynthesis.cancel()
    utteranceRef.current = null
    setIsSpeaking(false)
  }

  const playNarration = async (title: string, content: string) => {
    if (!window.speechSynthesis) {
      setError('Speech synthesis is not available in this browser.')
      return
    }

    setIsGenerating(true)
    setError(null)

    try {
      const response = await fetch(`${API_BASE}/gemini`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'narration', title, content }),
      })

      if (!response.ok) {
        throw new Error('Failed to generate narration text')
      }

      const payload = await response.json() as { data: { response: string } }
      const narrationText = payload.data.response

      // Now call the TTS endpoint for the generated text
      const ttsResponse = await fetch(`${API_BASE}/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: narrationText }),
      })

      if (ttsResponse.ok) {
        const ttsPayload = await ttsResponse.json() as { data: { audioBase64: string } }
        const audio = new Audio(`data:audio/wav;base64,${ttsPayload.data.audioBase64}`)
        
        audio.onplay = () => setIsSpeaking(true)
        audio.onended = () => setIsSpeaking(false)
        audio.onerror = () => {
          setIsSpeaking(false)
          setError('Audio playback failed')
        }

        await audio.play()
        return
      }

      // Fallback to browser TTS if backend TTS fails
      const utterance = new SpeechSynthesisUtterance(narrationText)
      utterance.rate = 0.95
      utterance.pitch = 1.02
      utterance.lang = 'en-IN'

      utterance.onend = () => {
        utteranceRef.current = null
        setIsSpeaking(false)
      }

      utterance.onerror = () => {
        utteranceRef.current = null
        setIsSpeaking(false)
        setError('Unable to play the narration right now.')
      }

      stopNarration()
      utteranceRef.current = utterance
      window.speechSynthesis.speak(utterance)
      setIsSpeaking(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to generate lesson narration.')
    } finally {
      setIsGenerating(false)
    }
  }

  return { playNarration, stopNarration, isSpeaking, isGenerating, error }
}