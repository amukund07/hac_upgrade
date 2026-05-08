import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, X, MessageSquare, Minimize2, Maximize2 } from 'lucide-react';
import { Card } from '../ui/Card';

type Message = {
  id: string;
  role: 'user' | 'elder';
  text: string;
};

export const ChatPopup = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'elder', text: 'Greetings, young one. I am the Keeper of Wisdom. What knowledge do you seek today?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isTyping, isOpen, isMinimized]);

  const handleSend = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    // Mock AI response
    setTimeout(() => {
      const elderMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'elder',
        text: 'The ancestors say: "He who learns, teaches." Your curiosity honors our traditions. Let me share a tale about that...'
      };
      setMessages(prev => [...prev, elderMsg]);
      setIsTyping(false);
    }, 2000);
  };

  const SUGGESTED_PROMPTS = [
    "Tell me a folk story about bravery.",
    "How was rainwater harvested in ancient times?",
    "What herbs help with digestion?",
  ];

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-4 pointer-events-none">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ 
              opacity: 1, 
              scale: 1, 
              y: 0,
              height: isMinimized ? '64px' : '500px'
            }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="w-[350px] md:w-[400px] pointer-events-auto"
          >
            <Card className="flex flex-col h-full p-0 overflow-hidden shadow-2xl border-earth-200/50 dark:border-earth-800/50 bg-white dark:bg-earth-900">
              {/* Header */}
              <div className="p-4 border-b border-earth-200 dark:border-earth-800 bg-earth-50 dark:bg-earth-950 flex items-center justify-between cursor-pointer" onClick={() => setIsMinimized(!isMinimized)}>
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-full bg-forest-100 dark:bg-forest-900/50 flex items-center justify-center">
                    <Sparkles className="h-4 w-4 text-forest-600 dark:text-forest-400" />
                  </div>
                  <div>
                    <h3 className="font-serif text-sm font-bold text-earth-900 dark:text-earth-50">Elder Spirit Guide</h3>
                    <div className="flex items-center gap-1">
                      <div className="h-1.5 w-1.5 rounded-full bg-green-500" />
                      <span className="text-[10px] text-earth-500 dark:text-earth-400 font-medium">Online</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button 
                    onClick={(e) => { e.stopPropagation(); setIsMinimized(!isMinimized); }}
                    className="p-1.5 text-earth-400 hover:text-earth-600 dark:hover:text-earth-200 transition-colors"
                  >
                    {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
                  </button>
                  <button 
                    onClick={(e) => { e.stopPropagation(); setIsOpen(false); }}
                    className="p-1.5 text-earth-400 hover:text-earth-600 dark:hover:text-earth-200 transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {!isMinimized && (
                <>
                  {/* Chat Area */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0 bg-paper-light/30 dark:bg-paper-dark/10">
                    {messages.map((msg) => (
                      <div
                        key={msg.id}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`max-w-[85%] rounded-2xl p-3 text-sm ${
                          msg.role === 'user' 
                            ? 'bg-forest-600 text-white rounded-br-sm shadow-sm' 
                            : 'bg-earth-100 dark:bg-earth-800 text-earth-900 dark:text-earth-100 rounded-bl-sm border border-earth-200 dark:border-earth-700'
                        }`}>
                          <p className="leading-relaxed">{msg.text}</p>
                        </div>
                      </div>
                    ))}
                    {isTyping && (
                      <div className="flex justify-start">
                        <div className="bg-earth-100 dark:bg-earth-800 rounded-2xl rounded-bl-sm p-3 flex gap-1 items-center">
                          <motion.div className="w-1.5 h-1.5 bg-earth-400 rounded-full" animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 0.6 }} />
                          <motion.div className="w-1.5 h-1.5 bg-earth-400 rounded-full" animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }} />
                          <motion.div className="w-1.5 h-1.5 bg-earth-400 rounded-full" animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }} />
                        </div>
                      </div>
                    )}
                    <div ref={endRef} />
                  </div>

                  {/* Input Area */}
                  <div className="p-4 border-t border-earth-200 dark:border-earth-800 bg-white dark:bg-earth-950">
                    {messages.length === 1 && (
                      <div className="flex flex-wrap gap-2 mb-3">
                        {SUGGESTED_PROMPTS.map((prompt, i) => (
                          <button
                            key={i}
                            onClick={() => setInput(prompt)}
                            className="text-[10px] px-2 py-1 rounded-full border border-earth-200 dark:border-earth-700 bg-earth-50 hover:bg-earth-100 dark:bg-earth-900 dark:hover:bg-earth-800 text-earth-700 dark:text-earth-300 transition-colors"
                          >
                            {prompt}
                          </button>
                        ))}
                      </div>
                    )}
                    
                    <form onSubmit={handleSend} className="flex gap-2">
                      <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask the Elder Guide..."
                        className="flex-1 bg-earth-50 dark:bg-earth-900 border border-earth-200 dark:border-earth-700 rounded-xl px-3 py-2 text-sm outline-none focus:border-forest-500 focus:ring-1 focus:ring-forest-500 text-earth-900 dark:text-earth-100 transition-all"
                      />
                      <button 
                        type="submit" 
                        disabled={!input.trim()}
                        className="p-2 bg-forest-600 text-white rounded-xl hover:bg-forest-700 disabled:opacity-50 transition-colors"
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

      {/* Floating Trigger Button */}
      {!isOpen && (
        <motion.button
          initial={{ scale: 0, rotate: -45 }}
          animate={{ scale: 1, rotate: 0 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setIsOpen(true)}
          className="h-14 w-14 rounded-full bg-forest-600 text-white shadow-xl flex items-center justify-center hover:bg-forest-700 transition-colors pointer-events-auto group relative"
        >
          <MessageSquare className="h-6 w-6" />
          <span className="absolute right-full mr-4 bg-earth-900 text-white text-xs px-3 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
            Ask Elder Guide
          </span>
          <div className="absolute -top-1 -right-1 h-4 w-4 bg-terracotta-500 rounded-full border-2 border-white dark:border-earth-900 flex items-center justify-center">
            <div className="h-1.5 w-1.5 rounded-full bg-white animate-pulse" />
          </div>
        </motion.button>
      )}
    </div>
  );
};
