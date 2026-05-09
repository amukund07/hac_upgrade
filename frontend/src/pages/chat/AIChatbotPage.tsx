import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Loader2, Send, Sparkles, Volume2 } from 'lucide-react'
import { Card } from '../../components/ui/Card'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:5000/api'

type Message = {
  id: string
  role: 'user' | 'elder'
  text: string
}

export const AIChatbotPage = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'elder', text: 'Greetings, young one. I am the Keeper of Wisdom. What knowledge do you seek today?' },
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  const handleSend = (event?: React.FormEvent) => {
    event?.preventDefault()

    if (!input.trim()) {
      return
    }

    const userMessage: Message = { id: Date.now().toString(), role: 'user', text: input }
    setMessages((previous) => [...previous, userMessage])
    const currentInput = input
    setInput('')
    setIsTyping(true)

    fetch(`${API_BASE}/chat/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: currentInput }),
    })
      .then((res) => res.json())
      .then((payload: { data: { response: string } }) => {
        const elderMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'elder',
          text: payload.data.response,
        }
        setMessages((previous) => [...previous, elderMessage])
        
        // Optionally speak the reply automatically
        void readLatestReply()
      })
      .catch(() => {
        setMessages((previous) => [...previous, {
          id: (Date.now() + 1).toString(),
          role: 'elder',
          text: 'I could not generate a response right now. Please try again in a moment.',
        }])
      })
      .finally(() => {
        setIsTyping(false)
      })
  }

  const readLatestReply = async () => {
    const latestReply = [...messages].reverse().find((message) => message.role === 'elder')

    if (!latestReply) {
      return
    }

    setIsSpeaking(true)

    try {
      const response = await fetch(`${API_BASE}/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: latestReply.text }),
      })

      if (response.ok) {
        const payload = await response.json() as { data?: { audioBase64?: string } }
        const audioBase64 = payload.data?.audioBase64

        if (audioBase64) {
          const audio = new Audio(`data:audio/wav;base64,${audioBase64}`)
          await audio.play()
          return
        }
      }

      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(latestReply.text)
        utterance.rate = 0.95
        utterance.pitch = 0.92
        window.speechSynthesis.cancel()
        window.speechSynthesis.speak(utterance)
      }
    } catch {
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(latestReply.text)
        utterance.rate = 0.95
        utterance.pitch = 0.92
        window.speechSynthesis.cancel()
        window.speechSynthesis.speak(utterance)
      }
    } finally {
      setIsSpeaking(false)
    }
  }

  const SUGGESTED_PROMPTS = [
    'Tell me a folk story about bravery.',
    'How was rainwater harvested in ancient times?',
    'What herbs help with digestion?',
  ]

  return (
    <div className="mx-auto flex h-[calc(100vh-4rem)] max-w-5xl flex-col px-4 py-4 md:px-6 md:py-6">
      <div className="mb-6 flex items-center gap-4 rounded-[28px] border border-terracotta-500/15 bg-gradient-to-r from-[#251812] via-[#21150f] to-[#170f0c] px-5 py-4 shadow-[0_18px_50px_rgba(0,0,0,0.28)]">
        <div className="flex h-16 w-16 items-center justify-center overflow-hidden rounded-full border border-terracotta-500/25 bg-gradient-to-br from-terracotta-500 to-burnt-orange-500 shadow-[0_0_18px_rgba(200,104,73,0.25)]">
          <img src="https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&q=80&w=200" alt="Elder Avatar" className="h-full w-full object-cover" />
        </div>
        <div>
          <h1 className="font-serif text-2xl font-bold text-cream">Elder Spirit Guide</h1>
          <p className="text-sm text-earth-100">Ask about traditions, nature, and history.</p>
        </div>
      </div>

      <Card className="flex flex-1 flex-col overflow-hidden rounded-[28px] border border-terracotta-500/15 bg-gradient-to-b from-[#231611] via-[#1d130f] to-[#170f0c] p-0 shadow-[0_22px_60px_rgba(0,0,0,0.28)]">
        <div className="flex-1 space-y-6 overflow-y-auto bg-[radial-gradient(circle_at_top,rgba(200,104,73,0.08),transparent_40%)] p-4 md:p-6">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-3xl p-4 text-sm leading-relaxed ${
                    message.role === 'user'
                      ? 'rounded-br-md bg-gradient-to-br from-terracotta-500 to-burnt-orange-500 text-white shadow-[0_14px_30px_rgba(200,104,73,0.2)]'
                      : 'rounded-bl-md border border-terracotta-500/15 bg-[#2d1f19] text-white shadow-[0_10px_28px_rgba(0,0,0,0.18)]'
                  }`}
                >
                  {message.role === 'elder' && <Sparkles className="mb-2 h-4 w-4 text-terracotta-300 opacity-80" />}
                  <p>{message.text}</p>
                </div>
              </motion.div>
            ))}

            {isTyping && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                <div className="flex h-12 items-center gap-1 rounded-2xl rounded-bl-md border border-terracotta-500/10 bg-[#2d1f19] px-4">
                  <motion.div className="h-2 w-2 rounded-full bg-terracotta-300" animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6 }} />
                  <motion.div className="h-2 w-2 rounded-full bg-terracotta-300" animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }} />
                  <motion.div className="h-2 w-2 rounded-full bg-terracotta-300" animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={endRef} />
        </div>

        <div className="border-t border-terracotta-500/10 bg-[#1a120e] p-4">
          {messages.length === 1 && (
            <div className="mb-4 flex flex-wrap gap-2">
              {SUGGESTED_PROMPTS.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => setInput(prompt)}
                  className="rounded-full border border-terracotta-500/15 bg-white/5 px-3 py-1.5 text-xs text-earth-200 transition-colors hover:border-terracotta-500/30 hover:bg-terracotta-500/10 hover:text-white md:text-sm"
                >
                  {prompt}
                </button>
              ))}
            </div>
          )}

          <form onSubmit={handleSend} className="flex gap-2">
            <button
              type="button"
              onClick={readLatestReply}
              disabled={isSpeaking}
              className="flex h-11 w-11 items-center justify-center rounded-xl border border-terracotta-500/15 bg-white/5 text-earth-200 transition-colors hover:border-terracotta-500/30 hover:bg-terracotta-500/10 hover:text-white disabled:opacity-60"
              aria-label="Listen to the latest guide reply"
            >
              {isSpeaking ? <Loader2 className="h-5 w-5 animate-spin" /> : <Volume2 className="h-5 w-5" />}
            </button>
            <input
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask the Elder Guide..."
              className="flex-1 rounded-xl border border-terracotta-500/15 bg-white/5 px-4 py-3 text-cream outline-none transition-all placeholder:text-earth-400 focus:border-terracotta-500/40 focus:ring-1 focus:ring-terracotta-500/20"
            />
            <button
              type="submit"
              disabled={!input.trim()}
              className="rounded-xl bg-gradient-to-r from-terracotta-500 to-burnt-orange-500 p-3 text-white transition-colors hover:from-terracotta-400 hover:to-burnt-orange-400 disabled:opacity-50"
            >
              <Send className="h-5 w-5" />
            </button>
          </form>
        </div>
      </Card>
    </div>
  )
}