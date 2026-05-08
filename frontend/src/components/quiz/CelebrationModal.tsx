import { AnimatePresence, motion } from 'framer-motion'
import { Award, Sparkles, Star } from 'lucide-react'
import { Card } from '../ui/Card'
import { Button } from '../ui/Button'

interface CelebrationModalProps {
  isOpen: boolean
  isCorrect: boolean
  xpGained: number
  onContinue: () => void
}

export const CelebrationModal = ({ isOpen, isCorrect, xpGained, onContinue }: CelebrationModalProps) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.95, y: 20 }}
            className="w-full max-w-md"
          >
            <Card className="relative overflow-hidden border-terracotta-400/30 bg-gradient-to-br from-earth-950 to-earth-900 p-8 text-center shadow-[0_24px_80px_rgba(0,0,0,0.35)]">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(200,104,73,0.18),transparent_40%)]" />

              <div className="relative">
                {isCorrect ? (
                  <>
                    <div className="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-terracotta-500 to-burnt-orange-500 shadow-[0_0_40px_rgba(200,104,73,0.35)]">
                      <Award className="h-12 w-12 text-white" />
                    </div>
                    <h2 className="mb-2 font-serif text-3xl font-bold text-cream">Wisdom Gained!</h2>
                    <p className="mb-6 text-earth-300">Your knowledge grows stronger and the next lesson is now unlocked.</p>
                    <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-antique-gold-400/30 bg-antique-gold-400/15 px-5 py-3 text-antique-gold-200">
                      <Star className="h-5 w-5 fill-current" />
                      <span className="text-xl font-medium">+{xpGained} XP</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full border-2 border-terracotta-400/30 bg-earth-900/80">
                      <Sparkles className="h-12 w-12 text-terracotta-300" />
                    </div>
                    <h2 className="mb-2 font-serif text-3xl font-bold text-cream">Keep Going</h2>
                    <p className="mb-8 text-earth-300">Every attempt sharpens the next one. Review the answers and try again.</p>
                  </>
                )}

                <Button onClick={onContinue} className="w-full bg-gradient-to-r from-terracotta-500 to-burnt-orange-500 text-white">
                  Continue Journey
                </Button>
              </div>
            </Card>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}