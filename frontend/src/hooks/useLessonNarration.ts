import { useEffect, useRef, useState } from 'react'
import { generateLessonNarration } from '../lib/gemini'

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
      const narration = await generateLessonNarration(title, content)
      const utterance = new SpeechSynthesisUtterance(narration)
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