import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";
import { Shield, Activity, UploadCloud, Terminal } from "lucide-react";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import AlertSystem from "./components/AlertSystem";
import AIAssistant from "./components/AIAssistant";
import { motion } from "framer-motion";

function Sidebar() {
  const location = useLocation();
  const navItems = [
    { path: "/", name: "Analytics Dashboard", icon: <Activity size={20} /> },
    { path: "/predict", name: "Threat Prediction", icon: <UploadCloud size={20} /> },
  ];

  return (
    <div className="w-64 h-screen glass-panel rounded-none border-t-0 border-b-0 border-l-0 flex flex-col p-6 z-10 relative">
      <div className="flex items-center gap-3 mb-12">
        <Shield className="text-cyber-primary" size={32} />
        <h1 className="text-2xl font-bold tracking-wider text-white">
          SENTINEL<span className="text-cyber-primary">NET</span>
        </h1>
      </div>
      
      <nav className="flex-1 space-y-4">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link key={item.path} to={item.path}>
              <motion.div
                whileHover={{ x: 5 }}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors cursor-pointer ${
                  isActive 
                    ? "bg-cyber-primary/20 text-cyber-primary border border-cyber-primary/30 shadow-[inset_0_0_10px_rgba(0,255,65,0.2)]" 
                    : "text-cyber-muted hover:text-white hover:bg-white/5"
                }`}
              >
                {item.icon}
                <span className="font-medium">{item.name}</span>
              </motion.div>
            </Link>
          );
        })}
      </nav>
      
      <div className="mt-auto border-t border-white/10 pt-6 text-sm text-cyber-muted flex items-center gap-2">
        <Terminal size={14} className="text-cyber-primary" />
        <span className="font-mono">SYS_STATUS: ONLINE</span>
      </div>
    </div>
  );
}

import AIExplanationPanel from "./components/AIExplanationPanel";

function App() {
  const [explanation, setExplanation] = useState({ isVisible: false, content: '', title: '' });

  useEffect(() => {
    const handleOpenExplanation = (e) => {
      setExplanation({
        isVisible: true,
        content: e.detail.content,
        title: e.detail.title
      });
    };

    window.addEventListener('open-ai-explanation', handleOpenExplanation);
    return () => window.removeEventListener('open-ai-explanation', handleOpenExplanation);
  }, []);

  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden selection:bg-cyber-primary/30">
        <Sidebar />
        <main className="flex-1 h-screen overflow-y-auto relative bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-opacity-5">
          {/* subtle grid overlay */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none"></div>
          
          <div className="p-8 relative z-10">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/predict" element={<Upload />} />
            </Routes>
          </div>
        </main>
        
        {/* Global Components */}
        <AlertSystem />
        <AIAssistant />
        <AIExplanationPanel 
          isVisible={explanation.isVisible} 
          onClose={() => setExplanation(prev => ({ ...prev, isVisible: false }))}
          content={explanation.content}
          title={explanation.title}
        />
      </div>
    </BrowserRouter>
  );
}

export default App;
