import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Loader2, Maximize2, MessageSquare, Minimize2, Send, Sparkles, Volume2, X } from 'lucide-react'
import { Card } from '../ui/Card'

type ChatMessage = {
  id: string
  role: 'user' | 'elder'
  text: string
}

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:5000/api'

export const ChatPopup = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: '1', role: 'elder', text: 'Greetings, young one. I am the Keeper of Wisdom. What knowledge do you seek today?' },
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isOpen && !isMinimized) {
      endRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isTyping, isOpen, isMinimized])

  const speakText = async (text: string) => {
    if (!text.trim()) {
      return
    }

    setIsSpeaking(true)

    try {
      const response = await fetch(`${API_BASE}/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })

      if (response.ok) {
        const payload = await response.json() as { data?: { audioBase64?: string } }
        const audioBase64 = payload.data?.audioBase64

        if (audioBase64) {
          const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`)
          await audio.play()
          return
        }
      }

      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.rate = 0.95
        utterance.pitch = 0.92
        window.speechSynthesis.cancel()
        window.speechSynthesis.speak(utterance)
      }
    } catch {
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.rate = 0.95
        utterance.pitch = 0.92
        window.speechSynthesis.cancel()
        window.speechSynthesis.speak(utterance)
      }
    } finally {
      setIsSpeaking(false)
    }
  }

  const readLatestGuideMessage = async () => {
    const latestElder = [...messages].reverse().find((message) => message.role === 'elder')
    if (latestElder) {
      await speakText(latestElder.text)
    }
  }

  const handleSend = (event?: React.FormEvent) => {
    event?.preventDefault()
    if (!input.trim()) return

    const userMessage: ChatMessage = { id: Date.now().toString(), role: 'user', text: input }
    setMessages((previous) => [...previous, userMessage])
    setInput('')
    setIsTyping(true)

    setTimeout(() => {
      const elderMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'elder',
        text: 'The ancestors say: "He who learns, teaches." Your curiosity honors our traditions. Let me share a tale about that...'
      }
      setMessages((previous) => [...previous, elderMessage])
      setIsTyping(false)
    }, 2000)
  }

  const SUGGESTED_PROMPTS = [
    'Tell me a folk story about bravery.',
    'How was rainwater harvested in ancient times?',
    'What herbs help with digestion?',
  ]

  return (
    <div className="pointer-events-none fixed bottom-6 right-6 z-50 flex flex-col items-end gap-4">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0, height: isMinimized ? '64px' : '500px' }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="pointer-events-auto w-[350px] md:w-[420px]"
          >
            <Card className="flex h-full flex-col overflow-hidden rounded-[28px] border border-terracotta-500/18 bg-gradient-to-b from-[#251812] via-[#21150f] to-[#170f0c] p-0 shadow-[0_28px_80px_rgba(0,0,0,0.45)] ring-1 ring-white/5">
              <div
                className="flex cursor-pointer items-center justify-between border-b border-terracotta-500/10 bg-white/5 px-4 py-4 backdrop-blur-md"
                onClick={() => setIsMinimized((value) => !value)}
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-terracotta-500 to-burnt-orange-500 shadow-[0_0_18px_rgba(200,104,73,0.25)]">
                    <Sparkles className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <h3 className="font-serif text-sm font-bold text-cream">Elder Spirit Guide</h3>
                    <div className="flex items-center gap-1">
                      <div className="h-1.5 w-1.5 rounded-full bg-green-500" />
                      <span className="text-[10px] font-medium text-earth-300">Online</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={(event) => {
                      event.stopPropagation()
                      setIsMinimized((value) => !value)
                    }}
                    className="p-1.5 text-earth-400 transition-colors hover:text-cream"
                  >
                    {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
                  </button>
                  <button
                    onClick={(event) => {
                      event.stopPropagation()
                      setIsOpen(false)
                    }}
                    className="p-1.5 text-earth-400 transition-colors hover:text-cream"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {!isMinimized && (
                <>
                  <div className="flex-1 min-h-0 space-y-4 overflow-y-auto bg-[radial-gradient(circle_at_top,rgba(200,104,73,0.10),transparent_40%)] p-4">
                    {messages.map((message) => (
                      <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div
                          className={`max-w-[85%] rounded-3xl p-3 text-sm leading-relaxed ${
                            message.role === 'user'
                              ? 'rounded-br-md bg-gradient-to-br from-terracotta-500 to-burnt-orange-500 text-white shadow-[0_14px_30px_rgba(200,104,73,0.22)]'
                              : 'rounded-bl-md border border-terracotta-500/15 bg-[#2d1f19] text-cream shadow-[0_10px_30px_rgba(0,0,0,0.18)]'
                          }`}
                        >
                          {message.role === 'elder' && <Sparkles className="mb-2 h-4 w-4 text-terracotta-300 opacity-80" />}
                          <p>{message.text}</p>
                        </div>
                      </div>
                    ))}

                    {isTyping && (
                      <div className="flex justify-start">
                        <div className="flex items-center gap-1 rounded-2xl rounded-bl-md border border-terracotta-500/10 bg-[#2d1f19] px-3 py-3">
                          <motion.div className="h-1.5 w-1.5 rounded-full bg-terracotta-300" animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 0.6 }} />
                          <motion.div className="h-1.5 w-1.5 rounded-full bg-terracotta-300" animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }} />
                          <motion.div className="h-1.5 w-1.5 rounded-full bg-terracotta-300" animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }} />
                        </div>
                      </div>
                    )}
                    <div ref={endRef} />
                  </div>

                  <div className="border-t border-terracotta-500/10 bg-[#1a120e] p-4">
                    {messages.length === 1 && (
                      <div className="mb-3 flex flex-wrap gap-2">
                        {SUGGESTED_PROMPTS.map((prompt, index) => (
                          <button
                            key={index}
                            onClick={() => setInput(prompt)}
                            className="rounded-full border border-terracotta-500/15 bg-white/5 px-3 py-1.5 text-[10px] text-earth-200 transition-colors hover:border-terracotta-500/30 hover:bg-terracotta-500/10 hover:text-white"
                          >
                            {prompt}
                          </button>
                        ))}
                      </div>
                    )}

                    <form onSubmit={handleSend} className="flex gap-2">
                      <button
                        type="button"
                        onClick={readLatestGuideMessage}
                        disabled={isSpeaking}
                        className="flex h-11 w-11 items-center justify-center rounded-xl border border-terracotta-500/15 bg-white/5 text-earth-200 transition-colors hover:border-terracotta-500/30 hover:bg-terracotta-500/10 hover:text-white disabled:opacity-60"
                        aria-label="Listen to the latest guide message"
                      >
                        {isSpeaking ? <Loader2 className="h-4 w-4 animate-spin" /> : <Volume2 className="h-4 w-4" />}
                      </button>
                      <input
                        type="text"
                        value={input}
                        onChange={(event) => setInput(event.target.value)}
                        placeholder="Ask the Elder Guide..."
                        className="flex-1 rounded-xl border border-terracotta-500/15 bg-white/5 px-3 py-2 text-sm text-cream outline-none transition-all placeholder:text-earth-400 focus:border-terracotta-500/40 focus:ring-1 focus:ring-terracotta-500/20"
                      />
                      <button
                        type="submit"
                        disabled={!input.trim()}
                        className="rounded-xl bg-gradient-to-r from-terracotta-500 to-burnt-orange-500 p-2.5 text-white transition-colors hover:from-terracotta-400 hover:to-burnt-orange-400 disabled:opacity-50"
                      >
                        <Send className="h-4 w-4" />
                      </button>
                    </form>
                  </div>
                </>
              )}
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {!isOpen && (
        <motion.button
          initial={{ scale: 0, rotate: -45 }}
          animate={{ scale: 1, rotate: 0 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setIsOpen(true)}
          className="group relative pointer-events-auto flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-terracotta-500 to-burnt-orange-500 text-white shadow-[0_14px_35px_rgba(200,104,73,0.35)] transition-colors hover:from-terracotta-400 hover:to-burnt-orange-400"
        >
          <MessageSquare className="h-6 w-6" />
          <span className="absolute right-full mr-4 whitespace-nowrap rounded-lg bg-[#1b120e] px-3 py-1.5 text-xs text-cream opacity-0 transition-opacity group-hover:opacity-100">
            Ask Elder Guide
          </span>
          <div className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full border-2 border-white bg-terracotta-500 dark:border-earth-900">
            <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-white" />
          </div>
        </motion.button>
      )}
    </div>
  )
}