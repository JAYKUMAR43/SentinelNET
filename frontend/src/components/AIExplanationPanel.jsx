import { motion, AnimatePresence } from 'framer-motion';
import { X, Bot, ShieldAlert, ChevronRight, Info } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function AIExplanationPanel({ isVisible, onClose, content, title }) {
  return (
    <AnimatePresence>
      {isVisible && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60]"
          />

          {/* Side Panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-screen w-full md:w-[500px] bg-cyber-bg border-l border-white/10 z-[70] flex flex-col shadow-[-10px_0_30px_rgba(0,0,0,0.5)]"
          >
            {/* Header */}
            <div className="p-6 border-b border-white/10 flex justify-between items-center bg-cyber-surface/30">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-cyber-primary/20 flex items-center justify-center border border-cyber-primary/40">
                  <Bot className="text-cyber-primary" size={24} />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white uppercase tracking-tight">AI Insights</h3>
                  <p className="text-xs text-cyber-muted font-mono">{title || "THREAT_ANALYSIS_CORE"}</p>
                </div>
              </div>
              <button 
                onClick={onClose}
                className="text-cyber-muted hover:text-white p-2 hover:bg-white/5 rounded-full transition-all"
              >
                <X size={24} />
              </button>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
              <div className="prose prose-invert max-w-none prose-p:text-cyber-text prose-headings:text-white prose-strong:text-cyber-accent">
                {content ? (
                  <div className="space-y-6">
                    <div className="bg-cyber-primary/5 border border-cyber-primary/20 rounded-xl p-4 flex items-start gap-3">
                      <ShieldAlert className="text-cyber-primary shrink-0" size={20} />
                      <p className="text-sm text-cyber-text italic leading-relaxed">
                        "I have analyzed the patterns and identified the following security implications. Review the mitigation steps below."
                      </p>
                    </div>
                    
                    <div className="text-cyber-text leading-relaxed font-sans prose-pre:bg-cyber-bg prose-pre:border prose-pre:border-white/10">
                       <ReactMarkdown>{content}</ReactMarkdown>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-cyber-muted opacity-50 space-y-4">
                    <Bot size={48} className="animate-pulse" />
                    <p className="font-mono text-sm uppercase tracking-widest">Waiting for data stream...</p>
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="p-6 border-t border-white/10 bg-cyber-surface/30">
              <button 
                onClick={onClose}
                className="w-full py-3 bg-cyber-primary/10 hover:bg-cyber-primary/20 text-cyber-primary font-bold rounded-lg border border-cyber-primary/30 transition-all flex items-center justify-center gap-2 group"
              >
                ACKNOWLEDGE & DISMISS
                <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
