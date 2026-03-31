import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, X, Send, Bot, User, Loader2 } from 'lucide-react';
import axios from 'axios';

export default function AIAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello Admin. I am Sentinel, your AI Security Assistant. Ask me anything about network security or threat mitigation.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await axios.post('http://127.0.0.1:8000/api/agent/chat', { message: userMsg.content });
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response || res.data.error }]);
    } catch (error) {
      const errorDetail = error.response?.data?.detail || "Error connecting to AI Secure Core. Ensure backend is running and NVIDIA API Key is set.";
      setMessages(prev => [...prev, { role: 'assistant', content: errorDetail }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-cyber-primary hover:bg-cyber-primary/80 text-black p-4 rounded-full shadow-glow-primary transition-all z-50 flex items-center gap-2 group"
      >
        <MessageSquare size={24} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            className="fixed bottom-24 right-6 w-96 h-[500px] glass-panel flex flex-col z-50 shadow-[0_0_30px_rgba(0,255,65,0.15)] overflow-hidden"
          >
            {/* Header */}
            <div className="bg-cyber-bg p-4 border-b border-cyber-primary/20 flex justify-between items-center relative overflow-hidden">
              <div className="absolute inset-x-0 bottom-0 h-[1px] bg-gradient-to-r from-transparent via-cyber-primary to-transparent" />
              <div className="flex items-center gap-2 text-white font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyber-primary to-cyber-accent">
                <Bot size={20} className="text-cyber-primary" /> Sentinel AI Agent
              </div>
              <button onClick={() => setIsOpen(false)} className="text-cyber-muted hover:text-white transition-colors">
                <X size={20} />
              </button>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-sm" style={{scrollbarWidth: 'thin'}}>
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-lg p-3 ${
                    msg.role === 'user' 
                      ? 'bg-cyber-primary/20 text-white border border-cyber-primary/50 rounded-br-none' 
                      : 'bg-cyber-bg/80 text-cyber-text border border-white/10 rounded-bl-none'
                  }`}>
                    {msg.role === 'assistant' && <Bot size={14} className="mb-1 text-cyber-primary" />}
                    {msg.role === 'user' && <User size={14} className="mb-1 text-cyber-accent ml-auto" />}
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-cyber-bg/80 border border-white/10 rounded-lg p-3 rounded-bl-none">
                    <Loader2 size={16} className="animate-spin text-cyber-primary" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <form onSubmit={handleSubmit} className="p-3 bg-cyber-bg border-t border-white/10 flex gap-2">
              <input 
                type="text" 
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Ask about vulnerabilities..." 
                className="flex-1 bg-cyber-surface border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyber-primary transition-colors"
              />
              <button 
                type="submit" 
                disabled={!input.trim() || isLoading}
                className="bg-cyber-primary/20 hover:bg-cyber-primary/40 text-cyber-primary p-2 rounded-lg border border-cyber-primary/50 transition-colors disabled:opacity-50"
              >
                <Send size={18} />
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
