import { useState, useCallback, useRef } from 'react'

interface UseWebSpeechTTSOptions {
  rate?: number
  pitch?: number
  volume?: number
}

export const useWebSpeechTTS = (options: UseWebSpeechTTSOptions = {}) => {
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null)

  // Check if Web Speech API is available
  const isSupported =
    typeof window !== 'undefined' &&
    ('speechSynthesis' in window ||
      'webkitSpeechSynthesis' in window)

  const speak = useCallback(
    (text: string) => {
      if (!isSupported) {
        const msg = 'Web Speech API is not supported in your browser'
        setError(msg)
        console.error(msg)
        return
      }

      if (!text || text.trim().length === 0) {
        setError('Text cannot be empty')
        return
      }

      try {
        setError(null)
        const synth = window.speechSynthesis

        // Cancel any ongoing speech
        synth.cancel()

        // Create utterance
        const utterance = new SpeechSynthesisUtterance(text)

        // Set properties
        utterance.rate = options.rate ?? 0.9 // Slightly slower for story feel
        utterance.pitch = options.pitch ?? 1.0
        utterance.volume = options.volume ?? 1.0

        // Try to set a nice voice
        const voices = synth.getVoices()
        const preferredVoice = voices.find(
          (v) => v.lang.startsWith('en') && v.name.includes('Google')
        ) || voices.find((v) => v.lang.startsWith('en'))

        if (preferredVoice) {
          utterance.voice = preferredVoice
        }

        // Event handlers
        utterance.onstart = () => {
          console.log('[Web Speech] Speaking started')
          setIsSpeaking(true)
        }

        utterance.onend = () => {
          console.log('[Web Speech] Speaking ended')
          setIsSpeaking(false)
        }

        utterance.onerror = (event) => {
          const errorMsg = `[Web Speech] Error: ${event.error}`
          console.error(errorMsg)
          setError(event.error)
          setIsSpeaking(false)
        }

        utteranceRef.current = utterance
        synth.speak(utterance)
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err)
        setError(errorMsg)
        console.error('[Web Speech] Exception:', errorMsg)
      }
    },
    [isSupported, options.rate, options.pitch, options.volume]
  )

  const stop = useCallback(() => {
    if (isSupported && window.speechSynthesis) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
      console.log('[Web Speech] Speaking stopped')
    }
  }, [isSupported])

  const pause = useCallback(() => {
    if (isSupported && window.speechSynthesis) {
      window.speechSynthesis.pause()
      console.log('[Web Speech] Speaking paused')
    }
  }, [isSupported])

  const resume = useCallback(() => {
    if (isSupported && window.speechSynthesis) {
      window.speechSynthesis.resume()
      console.log('[Web Speech] Speaking resumed')
    }
  }, [isSupported])

  return {
    speak,
    stop,
    pause,
    resume,
    isSpeaking,
    error,
    isSupported,
  }
}
