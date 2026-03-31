import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, Fingerprint, ActivitySquare, ShieldCheck, TrendingUp, RotateCcw } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, AreaChart, Area } from 'recharts';
import axios from 'axios';

const COLORS = ['#008f11', '#ff003c', '#ffb300', '#00ccff', '#ff00ff'];

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_scanned: 0,
    attacks_detected: 0,
    attack_percentage: 0,
    most_common_attack: "Loading...",
    threat_frequency: "N/A",
    distribution: [],
    history: [],
    threat_log: []
  });

  const fetchStats = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/stats');
      setStats(res.data);
    } catch (error) {
      console.error("Error fetching dashboard stats:", error);
    }
  };

  const handleReset = async () => {
    if (window.confirm("CRITICAL: This will PERMANENTLY clear all security logs and reset counters to zero. Proceed?")) {
      try {
        await axios.post('http://127.0.0.1:8000/api/stats/reset');
        fetchStats();
      } catch (error) {
        console.error("Error resetting stats:", error);
      }
    }
  };

  useEffect(() => {
    fetchStats();
    // Refresh every 1 second for true real-time feel (matches WebSocket popups)
    const interval = setInterval(fetchStats, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <header className="mb-8 flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2 uppercase tracking-tight">Security Analytics</h2>
          <div className="flex items-center gap-4">
            <p className="text-cyber-muted font-mono text-sm underline decoration-cyber-primary/30">REAL_TIME_THREAT_INTELLIGENCE_STREAM</p>
            <button 
              onClick={handleReset}
              className="text-[10px] bg-cyber-danger/20 hover:bg-cyber-danger/40 text-cyber-danger border border-cyber-danger/50 px-3 py-1 rounded-full flex items-center gap-1 transition-all font-bold animate-pulse"
            >
              <RotateCcw size={10} /> FORCE_SYSTEM_RESET
            </button>
          </div>
        </div>
        <div className="text-right hidden md:block">
          <p className="text-xs text-cyber-muted mb-1">NETWORK_NODE</p>
          <p className="text-sm font-mono text-cyber-primary">GW-01-SENTINEL</p>
        </div>
      </header>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <KPICard 
          title="Packets Analyzed" 
          value={stats.total_scanned.toLocaleString()} 
          icon={<ActivitySquare size={20} className="text-cyber-accent" />}
          delay={0.1}
        />
        <KPICard 
          title="Intrusions Blocked" 
          value={stats.attacks_detected.toLocaleString()} 
          icon={<ShieldAlert size={20} className="text-cyber-danger" />}
          glow="shadow-glow-danger"
          delay={0.2}
        />
        <KPICard 
          title="Threat Density" 
          value={`${stats.attack_percentage.toFixed(2)}%`} 
          icon={<TrendingUp size={20} className="text-cyber-warning" />}
          delay={0.3}
        />
        <KPICard 
          title="Frequency" 
          value={stats.threat_frequency} 
          icon={<ShieldCheck size={20} className="text-cyber-primary" />}
          delay={0.4}
        />
        <KPICard 
          title="Primary Vector" 
          value={stats.most_common_attack} 
          icon={<Fingerprint size={20} className="text-cyber-muted" />}
          delay={0.5}
        />
      </div>

      {/* Attack Timeline Graph */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass-panel p-6 h-[350px] flex flex-col"
      >
        <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
          <TrendingUp className="text-cyber-primary" /> Attack Timeline (Live)
        </h3>
        <div className="flex-1 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={stats.history}>
              <defs>
                <linearGradient id="colorAttacks" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00ff41" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#00ff41" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a3f54" vertical={false} />
              <XAxis 
                dataKey="time" 
                stroke="#8091a5" 
                tick={{fontSize: 10}}
                tickFormatter={(unixTime) => new Date(unixTime * 1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})} 
              />
              <YAxis stroke="#8091a5" tick={{fontSize: 10}} />
              <RechartsTooltip 
                contentStyle={{ backgroundColor: '#121a21', borderColor: '#00ff41', borderRadius: '8px' }}
                labelFormatter={(label) => new Date(label * 1000).toLocaleString()}
              />
              <Area type="monotone" dataKey="attacks" stroke="#00ff41" fillOpacity={1} fill="url(#colorAttacks)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        {/* Pie Chart Component */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6 }}
          className="glass-panel p-6 h-[400px] flex flex-col"
        >
          <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <ShieldAlert className="text-cyber-warning" /> Traffic Distribution
          </h3>
          <div className="flex-1 w-full min-h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats.distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {stats.distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#121a21', borderColor: '#00ff41', borderRadius: '8px' }}
                  itemStyle={{ color: '#00ff41' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Bar Chart Component */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.7 }}
          className="glass-panel p-6 h-[400px] flex flex-col"
        >
          <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <ActivitySquare className="text-cyber-accent" /> Attack Frequencies
          </h3>
          <div className="flex-1 w-full min-h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.distribution.filter(d => d.name !== 'Normal')} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a3f54" vertical={false} />
                <XAxis dataKey="name" stroke="#8091a5" />
                <YAxis stroke="#8091a5" />
                <RechartsTooltip cursor={{fill: 'rgba(255, 255, 255, 0.05)'}} contentStyle={{ backgroundColor: '#121a21', borderColor: '#ff003c', borderRadius: '8px' }} />
                <Bar dataKey="value" fill="#ff003c" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Real-time Threat Stream Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="glass-panel p-6 mt-8"
      >
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold flex items-center gap-2">
            <ActivitySquare className="text-cyber-primary" /> Network Intrusion Logs
          </h3>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-cyber-primary rounded-full animate-ping" />
            <span className="text-[10px] font-mono text-cyber-muted uppercase tracking-widest">Live Flow</span>
          </div>
        </div>
        
        <div className="max-h-[600px] overflow-y-auto pr-2">
          <table className="w-full text-left border-separate border-spacing-y-2">
            <thead className="text-cyber-muted text-[10px] uppercase tracking-widest font-mono sticky top-0 bg-cyber-surface z-10">
              <tr className="bg-cyber-surface">
                <th className="py-4 px-4">Timestamp</th>
                <th className="py-4 px-4">Traffic Type</th>
                <th className="py-4 px-4">Origin Node</th>
                <th className="py-4 px-4">Status</th>
                <th className="py-4 px-4">Risk Percent</th>
                <th className="py-4 px-4 text-right">Protection</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {stats.threat_log && stats.threat_log.length > 0 ? (
                stats.threat_log.map((log, idx) => (
                  <motion.tr 
                    layout
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    key={`${log.timestamp}-${idx}`}
                    className="bg-cyber-bg/40 hover:bg-cyber-surface/50 transition-all border border-white/5 rounded-lg group"
                  >
                    <td className="py-4 px-4 font-mono text-cyber-muted text-xs">{log.timestamp}</td>
                    <td className="py-4 px-4 font-bold text-white tracking-tight">{log.type}</td>
                    <td className="py-4 px-4 font-mono text-[11px] text-cyber-accent/70">{log.source}</td>
                    <td className="py-4 px-4">
                      <span className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-tighter shadow-sm ${
                        log.status === 'Normal' 
                          ? 'bg-cyber-primary/10 text-cyber-primary border border-cyber-primary/20' 
                          : 'bg-cyber-danger/20 text-cyber-danger border border-cyber-danger/30 shadow-glow-danger animate-pulse'
                      }`}>
                        {log.status === 'Normal' ? 'Normal' : 'Intrusion'}
                      </span>
                    </td>
                    <td className="py-4 px-4 font-mono text-cyber-accent text-xs">{log.confidence}</td>
                    <td className="py-4 px-4 text-right">
                      <span className={`text-[10px] font-mono px-2 py-1 rounded border ${
                        log.status === 'Normal' 
                          ? 'text-cyber-muted border-white/10' 
                          : 'text-cyber-danger border-cyber-danger/50 bg-cyber-danger/5'
                      }`}>
                        {log.status === 'Normal' ? 'NONE' : 'QUARANTINE'}
                      </span>
                    </td>
                  </motion.tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="py-12 text-center text-cyber-muted italic font-mono text-xs uppercase tracking-widest">
                    Securing Perimeter... Monitoring network activity
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </motion.div>
    </motion.div>
  );
}

function KPICard({ title, value, icon, delay, glow }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className={`glass-panel p-6 relative overflow-hidden group ${glow ? glow : ''}`}
    >
      <div className="absolute top-0 right-0 p-4 opacity-20 group-hover:opacity-40 transition-opacity">
        {icon}
      </div>
      <p className="text-cyber-muted font-medium mb-1">{title}</p>
      <h3 className="text-3xl font-bold font-mono text-white">{value}</h3>
      <div className="w-12 h-1 bg-cyber-primary/50 mt-4 group-hover:w-full group-hover:bg-cyber-primary transition-all duration-500 rounded-full" />
    </motion.div>
  );
}
