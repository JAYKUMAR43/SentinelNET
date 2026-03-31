import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertOctagon, X } from 'lucide-react';

export default function AlertSystem() {
  const [alerts, setAlerts] = useState([]);
  const audioRef = useRef(null);

  useEffect(() => {
    // We create a temporary audio object to play the alarm sound immediately
    // In a real production app, this would be a local asset
    audioRef.current = new Audio('https://actions.google.com/sounds/v1/alarms/spaceship_alarm.ogg');
    audioRef.current.volume = 0.5;

    // Connect to WebSocket using native browser API
    // Ensure this matches FastAPI port
    const socket = new WebSocket('ws://127.0.0.1:8000/api/realtime/ws');

    socket.onopen = () => {
      console.log('Connected to Real-time IDS Engine');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.threat_detected && data.packets) {
        // Process batch of packets
        data.packets.forEach(packet => {
          if (packet.prediction !== 'normal') {
            const newAlert = {
              id: packet.timestamp || Date.now(),
              type: packet.prediction,
              source: packet.source_ip,
              protocol: packet.protocol
            };
            
            setAlerts((prev) => [...prev, newAlert]);
            
            // Play sound on Attack Detected
            try {
              audioRef.current.currentTime = 0;
              audioRef.current.play();
            } catch (e) {
              console.error("Audio playback blocked by browser.", e);
            }

            // Auto remove alert after 8 seconds
            setTimeout(() => {
              setAlerts((prev) => prev.filter(a => a.id !== newAlert.id));
            }, 8000);
          }
        });
      }
    };

    return () => {
      socket.close();
    };
  }, []);

  const dismissAlert = (id) => {
    setAlerts((prev) => prev.filter(a => a.id !== id));
  };

  return (
    <div className="fixed top-6 right-6 z-50 flex flex-col gap-3 pointer-events-none w-80">
      <AnimatePresence>
        {alerts.map((alert) => (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, x: 50, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 50, scale: 0.9, transition: { duration: 0.2 } }}
            className="pointer-events-auto bg-cyber-bg border border-cyber-danger shadow-glow-danger rounded-xl p-4 overflow-hidden relative"
          >
            {/* Flashing Background Effect */}
            <motion.div 
              animate={{ opacity: [0, 0.15, 0] }}
              transition={{ repeat: Infinity, duration: 1 }}
              className="absolute inset-0 bg-cyber-danger"
            />
            
            <div className="relative flex justify-between items-start">
              <div className="flex items-center gap-3 text-cyber-danger font-bold mb-2">
                <AlertOctagon className="animate-pulse" /> THREAT DETECTED
              </div>
              <button onClick={() => dismissAlert(alert.id)} className="text-white/50 hover:text-white transition-colors">
                <X size={16} />
              </button>
            </div>
            
            <div className="relative font-mono text-xs text-white/80 space-y-1 mt-2">
              <p><span className="text-cyber-danger">Vector:</span> {alert.type}</p>
              <p><span className="text-cyber-muted">Source IP:</span> {alert.source}</p>
              <p><span className="text-cyber-muted">Protocol:</span> {alert.protocol}</p>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
