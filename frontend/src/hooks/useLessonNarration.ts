import { useEffect, useRef, useState } from 'react'
import { getModuleLessons } from '../services/moduleService'
import { synthesizeNarration } from '../services/ttsService'
import { buildNarrationPrompt, splitNarrationIntoChunks, type NarrationChunk } from '../utils/storyNarration'

export const useLessonNarration = () => {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const cacheRef = useRef<Map<string, string>>(new Map())
  const chunksRef = useRef<NarrationChunk[]>([])
  const runIdRef = useRef(0)
  const resumeIndexRef = useRef(0)
  const speedRef = useRef(0.95)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [speed, setSpeed] = useState(0.95)
  const [activeChunkIndex, setActiveChunkIndex] = useState(-1)
  const [activeParagraphIndex, setActiveParagraphIndex] = useState(0)
  const [currentSubtitle, setCurrentSubtitle] = useState('')
  const [chunks, setChunks] = useState<NarrationChunk[]>([])

  useEffect(() => {
    speedRef.current = speed
  }, [speed])

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.src = ''
      }
    }
  }, [])

  const stopNarration = () => {
    runIdRef.current += 1

    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.src = ''
      audioRef.current = null
    }

    if (activeChunkIndex >= 0) {
      resumeIndexRef.current = activeChunkIndex + 1
    }

    setIsSpeaking(false)
    setIsGenerating(false)
    setActiveChunkIndex(-1)
    setActiveParagraphIndex(0)
    setCurrentSubtitle('')
  }

  const buildModuleNarrationChunks = (title: string, content: string, moduleLessons: Array<{ title: string; content: string }>) => {
    const lessonChunks = splitNarrationIntoChunks(title, content)

    return lessonChunks.map((chunk, index) => {
      if (index === 0) {
        return {
          ...chunk,
          text: `Now, beta... settle in softly. This lesson is one of ${Math.max(moduleLessons.length, 1)} steps in our journey through ${title}.`,
        }
      }

      return chunk
    })
  }

  const ensureChunkAudio = async (chunk: NarrationChunk) => {
    const cacheKey = chunk.id
    const cachedAudio = cacheRef.current.get(cacheKey)

    if (cachedAudio) {
      console.log(`[Narration] Using cached audio for chunk: ${cacheKey}`)
      return cachedAudio
    }

    console.log(`[Narration] Synthesizing new audio for chunk: ${cacheKey}`)
    const response = await synthesizeNarration({
      text: buildNarrationPrompt(chunk),
      style: 'story',
    })

    console.log(`[Narration] Synthesis response:`, { error: response.error, audioLength: response.data?.audioBase64?.length })

    if (response.error || !response.data?.audioBase64) {
      console.error(`[Narration] Synthesis failed:`, response.error)
      throw new Error(response.error ?? 'Unable to generate lesson narration.')
    }

    cacheRef.current.set(cacheKey, response.data.audioBase64)
    return response.data.audioBase64
  }

  const playChunks = async (startIndex: number, narrationChunks: NarrationChunk[]) => {
    const currentRun = ++runIdRef.current
    setError(null)
    setIsGenerating(true)
    setIsSpeaking(true)

    try {
      for (let index = startIndex; index < narrationChunks.length; index += 1) {
        if (runIdRef.current !== currentRun) {
          return
        }

        const chunk = narrationChunks[index]
        const nextChunk = narrationChunks[index + 1]
        setActiveChunkIndex(index)
        setActiveParagraphIndex(chunk.paragraphIndex)
        setCurrentSubtitle(chunk.text)

        const currentAudioPromise = ensureChunkAudio(chunk)
        const preloadNext = nextChunk ? ensureChunkAudio(nextChunk).catch(() => undefined) : null
        const audioBase64 = await currentAudioPromise

        if (runIdRef.current !== currentRun) {
          return
        }

        // Handle both WAV and MP3 formats
        // If audioBase64 starts with 'data:', it already has MIME type
        // Otherwise, default to WAV format for backward compatibility
        console.log(`[Narration] Audio data preview:`, audioBase64.substring(0, 50))
        const audioSrc = audioBase64.startsWith('data:')
          ? audioBase64
          : `data:audio/wav;base64,${audioBase64}`

        console.log(`[Narration] Creating Audio element with src:`, audioSrc.substring(0, 50))
        const audio = new Audio(audioSrc)
        audioRef.current = audio
        audio.playbackRate = speedRef.current

        audio.addEventListener('play', () => console.log(`[Narration] Audio started playing`))
        audio.addEventListener('pause', () => console.log(`[Narration] Audio paused`))
        audio.addEventListener('ended', () => console.log(`[Narration] Audio ended`))
        audio.addEventListener('error', (e) => console.error(`[Narration] Audio error:`, e))

        await new Promise<void>((resolve, reject) => {
          audio.addEventListener('ended', () => resolve(), { once: true })
          audio.addEventListener('error', () => reject(new Error('Unable to continue narration playback.')), { once: true })
          void audio.play().catch(reject)
        })

        if (preloadNext) {
          void preloadNext
        }

        resumeIndexRef.current = index + 1
      }
    } catch (err) {
      if (runIdRef.current === currentRun) {
        setError(err instanceof Error ? err.message : 'Unable to generate lesson narration.')
      }
    } finally {
      if (runIdRef.current === currentRun) {
        setIsGenerating(false)
        setIsSpeaking(false)
        setActiveChunkIndex(-1)
        setActiveParagraphIndex(0)
        setCurrentSubtitle('')
      }
    }
  }

  const playNarration = async (moduleId: string, title: string, content: string) => {
    stopNarration()
    setIsGenerating(true)
    setError(null)

    try {
      const lessonsResult = await getModuleLessons(moduleId)
      const narrationChunks = buildModuleNarrationChunks(title, content, lessonsResult.data ?? [])
      chunksRef.current = narrationChunks
      setChunks(narrationChunks)
      resumeIndexRef.current = 0
      await playChunks(0, narrationChunks)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to generate lesson narration.')
      setIsGenerating(false)
      setIsSpeaking(false)
    }
  }

  const resumeNarration = async () => {
    const narrationChunks = chunksRef.current

    if (!narrationChunks.length) {
      setError('There is no narration to continue yet.')
      return
    }

    await playChunks(Math.min(resumeIndexRef.current, narrationChunks.length - 1), narrationChunks)
  }

  return {
    playNarration,
    stopNarration,
    resumeNarration,
    isSpeaking,
    isGenerating,
    error,
    activeChunkIndex,
    activeParagraphIndex,
    currentSubtitle,
    chunks,
    speed,
    setSpeed,
    progress: chunks.length > 0 && activeChunkIndex >= 0 ? ((activeChunkIndex + 1) / chunks.length) * 100 : 0,
    canResume: resumeIndexRef.current > 0 && resumeIndexRef.current < chunks.length,
  }
}