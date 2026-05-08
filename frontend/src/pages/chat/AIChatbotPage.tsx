import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Mic, Sparkles } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { generateRAGResponse } from '../../lib/gemini';

type Message = {
  id: string;
  role: 'user' | 'elder';
  text: string;
};

export const AIChatbotPage = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'elder', text: 'Greetings, young one. I am the Keeper of Wisdom. What knowledge do you seek today?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    void generateRAGResponse(input, [])
      .then((reply) => {
        const elderMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: 'elder',
          text: reply,
        };
        setMessages(prev => [...prev, elderMsg]);
      })
      .catch(() => {
        setMessages(prev => [...prev, {
          id: (Date.now() + 1).toString(),
          role: 'elder',
          text: 'I could not generate a response right now. Please try again in a moment.',
        }]);
      })
      .finally(() => {
        setIsTyping(false);
      });
  };

  const SUGGESTED_PROMPTS = [
    "Tell me a folk story about bravery.",
    "How was rainwater harvested in ancient times?",
    "What herbs help with digestion?",
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-4xl mx-auto p-4 md:p-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <div className="h-16 w-16 rounded-full bg-earth-200 dark:bg-earth-800 flex items-center justify-center border-2 border-earth-300 dark:border-earth-700 overflow-hidden shadow-inner">
           <img src="https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&q=80&w=200" alt="Elder Avatar" className="w-full h-full object-cover" />
        </div>
        <div>
          <h1 className="font-serif text-2xl font-bold text-earth-900 dark:text-earth-50">Elder Spirit Guide</h1>
          <p className="text-sm text-earth-600 dark:text-earth-400">Ask about traditions, nature, and history.</p>
        </div>
      </div>

      {/* Chat Area */}
      <Card className="flex-1 flex flex-col p-0 overflow-hidden bg-white/50 dark:bg-earth-900/20 backdrop-blur-sm border-earth-200/50 dark:border-earth-800/50">
        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
          <AnimatePresence>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] md:max-w-[70%] rounded-2xl p-4 ${
                  msg.role === 'user' 
                    ? 'bg-forest-600 text-white rounded-br-sm shadow-md' 
                    : 'bg-earth-100 dark:bg-earth-800 text-earth-900 dark:text-earth-100 rounded-bl-sm shadow-sm'
                }`}>
                  {msg.role === 'elder' && <Sparkles className="h-4 w-4 mb-2 text-earth-500 opacity-50" />}
                  <p className="leading-relaxed">{msg.text}</p>
                </div>
              </motion.div>
            ))}
            {isTyping && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="bg-earth-100 dark:bg-earth-800 rounded-2xl rounded-bl-sm p-4 flex gap-1 items-center h-12">
                  <motion.div className="w-2 h-2 bg-earth-400 rounded-full" animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6 }} />
                  <motion.div className="w-2 h-2 bg-earth-400 rounded-full" animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }} />
                  <motion.div className="w-2 h-2 bg-earth-400 rounded-full" animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={endRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-earth-200 dark:border-earth-800 bg-white dark:bg-earth-950">
          {messages.length === 1 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {SUGGESTED_PROMPTS.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => setInput(prompt)}
                  className="text-xs md:text-sm px-3 py-1.5 rounded-full border border-earth-200 dark:border-earth-700 bg-earth-50 hover:bg-earth-100 dark:bg-earth-900 dark:hover:bg-earth-800 text-earth-700 dark:text-earth-300 transition-colors"
                >
                  {prompt}
                </button>
              ))}
            </div>
          )}
          
          <form onSubmit={handleSend} className="flex gap-2">
            <button type="button" className="p-3 text-earth-500 hover:bg-earth-100 rounded-xl dark:hover:bg-earth-800 transition-colors">
              <Mic className="h-5 w-5" />
            </button>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask the Elder Guide..."
              className="flex-1 bg-earth-50 dark:bg-earth-900 border border-earth-200 dark:border-earth-700 rounded-xl px-4 py-3 outline-none focus:border-forest-500 focus:ring-1 focus:ring-forest-500 text-earth-900 dark:text-earth-100 transition-all"
            />
            <button 
              type="submit" 
              disabled={!input.trim()}
              className="p-3 bg-forest-600 text-white rounded-xl hover:bg-forest-700 disabled:opacity-50 disabled:hover:bg-forest-600 transition-colors"
            >
              <Send className="h-5 w-5" />
            </button>
          </form>
        </div>
      </Card>
    </div>
  );
};
