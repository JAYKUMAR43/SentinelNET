import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, FileText, Download, AlertTriangle, CheckCircle, Terminal, ShieldCheck, Bot } from 'lucide-react';
import axios from 'axios';

export default function Upload() {
  const [mode, setMode] = useState('bulk'); // 'bulk' | 'single'
  const [file, setFile] = useState(null);
  const [singleInput, setSingleInput] = useState('');
  const [status, setStatus] = useState('idle'); // idle, loading, success, error
  const [errorMessage, setErrorMessage] = useState('');
  const [result, setResult] = useState(null);

  const handleFileUpload = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const submitPrediction = async () => {
    setStatus('loading');
    setErrorMessage('');
    setResult(null);

    try {
      if (mode === 'bulk') {
        if (!file) throw new Error("Please select a CSV file first.");
        
        const formData = new FormData();
        formData.append('file', file);
        
        const res = await axios.post(`${import.meta.env.VITE_API_URL}/api/predict/bulk`, formData);
        
        if (res.data.status === 'error') {
          throw new Error(res.data.message);
        }
        setResult(res.data);
      } else {
        if (!singleInput.trim()) throw new Error("Features input cannot be empty.");
        let features;
        try {
          features = JSON.parse(singleInput);
        } catch (e) {
          throw new Error("Invalid JSON format. Please provide valid object.");
        }
        
        const res = await axios.post(`${import.meta.env.VITE_API_URL}/api/predict/single`, { features });
        if (res.data.status === 'error') throw new Error(res.data.message);
        setResult(res.data);
      }
      setStatus('success');
    } catch (error) {
      console.error(error);
      setStatus('error');
      setErrorMessage(error.response?.data?.detail || error.message || "An unknown error occurred.");
    }
  };

  const downloadReport = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sentinel_report_${new Date().getTime()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-4xl mx-auto space-y-6">
      <header className="mb-8 border-b border-white/10 pb-4">
        <h2 className="text-3xl font-bold text-white mb-2">Threat Prediction Engine</h2>
        <p className="text-cyber-muted">Upload bulk traffic logs (CSV) or input manual packet features.</p>
      </header>
      
      {/* Mode Toggle */}
      <div className="flex bg-cyber-bg/50 p-1 rounded-xl w-max border border-white/10 mb-8">
        <button 
          onClick={() => setMode('bulk')}
          className={`px-6 py-2 rounded-lg font-medium transition-all ${mode === 'bulk' ? 'bg-cyber-surface shadow-glow-primary text-cyber-primary' : 'text-cyber-muted hover:text-white'}`}
        >
          Bulk Upload (CSV)
        </button>
        <button 
          onClick={() => setMode('single')}
          className={`px-6 py-2 rounded-lg font-medium transition-all ${mode === 'single' ? 'bg-cyber-surface shadow-glow-primary text-cyber-primary' : 'text-cyber-muted hover:text-white'}`}
        >
          Manual Entry (JSON)
        </button>
      </div>

      <div className="glass-panel p-8">
        {mode === 'bulk' ? (
          <div className="space-y-6">
            <div className={`border-2 border-dashed ${file ? 'border-cyber-primary bg-cyber-primary/5' : 'border-cyber-muted hover:border-cyber-accent hover:bg-cyber-accent/5'} rounded-xl p-12 text-center transition-all`}>
              <UploadCloud size={48} className={`mx-auto mb-4 ${file ? 'text-cyber-primary' : 'text-cyber-muted'}`} />
              <input type="file" id="file-upload" accept=".csv" className="hidden" onChange={handleFileUpload} />
              <label htmlFor="file-upload" className="cursor-pointer block">
                <span className="text-lg font-medium text-white block mb-2">{file ? file.name : 'Select CSV Layout'}</span>
                <span className="text-sm text-cyber-muted">{file ? 'Click to change file' : 'Drag and drop or click to browse'}</span>
              </label>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <label className="text-sm font-medium text-cyber-muted flex items-center gap-2">
              <Terminal size={16} /> JSON Feature Vector
            </label>
            <textarea 
              value={singleInput}
              onChange={(e) => setSingleInput(e.target.value)}
              className="w-full h-48 bg-cyber-bg/80 border border-white/10 rounded-xl p-4 text-cyber-primary font-mono text-sm focus:outline-none focus:border-cyber-primary transition-colors"
              placeholder={'{\n  "duration": 0,\n  "protocol_type": "tcp",\n  "service": "http",\n  "flag": "SF",\n  "src_bytes": 181,\n  "dst_bytes": 5450\n}'}
            />
          </div>
        )}

        <div className="mt-8 flex justify-end">
          <button 
            onClick={submitPrediction}
            disabled={status === 'loading'}
            className="btn-primary w-full md:w-auto flex justify-center items-center gap-2"
          >
            {status === 'loading' ? (
              <span className="animate-pulse">Processing...</span>
            ) : (
              <>
                <ShieldCheck size={20} /> ANALYZE TRAFFIC
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results & Error Handling - Specific fix layout */}
      <AnimatePresence>
        {status === 'error' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="glass-panel border-cyber-danger bg-cyber-danger/10 p-6 flex flex-col gap-2">
            <div className="flex items-center gap-3 text-cyber-danger font-bold text-lg">
              <AlertTriangle size={24} /> ANALYSIS FAILED
            </div>
            <p className="text-white/80 font-mono text-sm">{errorMessage}</p>
          </motion.div>
        )}

        {status === 'success' && result && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="glass-panel border-cyber-primary bg-cyber-primary/5 p-6 relative">
            <div className="flex justify-between items-start mb-6">
              <div className="flex items-center gap-3 text-cyber-primary font-bold text-xl">
                <CheckCircle size={28} /> ANALYSIS COMPLETE
              </div>
              {mode === 'bulk' && (
                <button onClick={downloadReport} className="flex items-center gap-2 text-sm text-cyber-accent hover:text-white transition-colors bg-cyber-surface px-3 py-1.5 rounded-lg border border-white/10 hover:border-cyber-accent">
                  <Download size={16} /> Download Report
                </button>
              )}
            </div>
            
            {mode === 'bulk' ? (
              <div className="space-y-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="bg-cyber-bg/50 p-4 rounded-lg">
                    <p className="text-cyber-muted text-sm">Total Records</p>
                    <p className="text-2xl font-mono text-white">{result.total_records}</p>
                  </div>
                  <div className="bg-cyber-danger/20 p-4 rounded-lg border border-cyber-danger/30">
                    <p className="text-cyber-muted text-sm text-cyber-danger">Attacks Detected</p>
                    <p className="text-2xl font-mono text-cyber-danger font-bold">{result.attacks_detected}</p>
                  </div>
                  <div className="bg-cyber-primary/10 p-4 rounded-lg border border-cyber-primary/20">
                    <p className="text-cyber-muted text-sm text-cyber-primary">Normal Traffic</p>
                    <p className="text-2xl font-mono text-cyber-primary font-bold">{result.normal_traffic}</p>
                  </div>
                  <div className={`p-4 rounded-lg border flex flex-col justify-center ${
                    result.risk_level === 'High' ? 'bg-cyber-danger/30 border-cyber-danger' : 
                    result.risk_level === 'Medium' ? 'bg-cyber-warning/30 border-cyber-warning' : 
                    'bg-cyber-primary/30 border-cyber-primary'
                  }`}>
                    <p className="text-cyber-muted text-xs uppercase tracking-wider mb-1">Risk Level</p>
                    <p className={`text-xl font-bold font-mono ${
                      result.risk_level === 'High' ? 'text-cyber-danger' : 
                      result.risk_level === 'Medium' ? 'text-cyber-warning' : 
                      'text-cyber-primary'
                    }`}>{result.risk_level}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-cyber-bg/40 p-5 rounded-xl border border-white/5">
                    <h4 className="text-sm font-bold text-white mb-4 uppercase tracking-widest flex items-center gap-2">
                      <ShieldCheck size={14} className="text-cyber-primary" /> Confidence Analytics
                    </h4>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-cyber-muted">AVG_CONFIDENCE</span>
                          <span className="text-white">
                            {((result.average_confidence || 0) * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-cyber-primary transition-all duration-1000" 
                            style={{ width: `${(result.average_confidence || 0) * 100}%` }}
                          />
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-cyber-muted">LOW_CONF_RATIO</span>
                          <span className={`font-bold ${(result.low_confidence_percentage || 0) > 30 ? 'text-cyber-danger' : 'text-cyber-warning'}`}>
                            {result.low_confidence_percentage || 0}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-cyber-bg/40 p-5 rounded-xl border border-white/5 group">
                    <h4 className="text-sm font-bold text-white mb-4 uppercase tracking-widest flex items-center gap-2">
                      <AlertTriangle size={14} className="text-cyber-warning" /> Top Threat Classes
                    </h4>
                    <div className="space-y-2">
                      {result.attack_distribution && Object.entries(result.attack_distribution)
                        .filter(([name]) => name.toLowerCase() !== 'normal')
                        .sort((a, b) => b[1] - a[1])
                        .slice(0, 3)
                        .map(([name, count], idx) => (
                        <div key={idx} className="flex justify-between items-center bg-white/5 p-2 rounded border border-white/5 group-hover:border-cyber-primary/30 transition-all">
                          <span className="text-white text-xs font-mono">{name}</span>
                          <span className="text-cyber-primary font-bold text-xs">{count}</span>
                        </div>
                      ))}
                      {(!result.attack_distribution || Object.keys(result.attack_distribution).length <= 1) && (
                        <p className="text-cyber-muted italic text-[10px] py-4 text-center">No threats identified.</p>
                      )}
                    </div>
                  </div>

                  <div className="bg-cyber-bg/40 p-5 rounded-xl border border-white/5 flex flex-col justify-between">
                    <div>
                      <h4 className="text-sm font-bold text-white mb-4 uppercase tracking-widest flex items-center gap-2">
                        <Terminal size={14} className="text-cyber-accent" /> System Summary
                      </h4>
                      <div className="space-y-3 font-mono text-xs">
                        <div className="flex justify-between">
                          <span className="text-cyber-muted">THREAT_LEVEL:</span>
                          <span className={`font-bold ${result.risk_level === 'High' ? 'text-cyber-danger' : result.risk_level === 'Medium' ? 'text-cyber-warning' : 'text-cyber-primary'}`}>{result.attack_percentage}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-cyber-muted">TOTAL_RECORDS:</span>
                          <span className="text-white">{result.total_records}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-cyber-muted">PRIMARY_VECTOR:</span>
                          <span className="text-cyber-warning">{result.most_common_attack}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-cyber-bg/50 p-6 rounded-lg border border-white/5 flex flex-col items-center">
                <p className="text-cyber-muted text-sm mb-2">Classification Result</p>
                <div className={`px-6 py-3 rounded-xl border ${result.result.attack_type === 'Normal' ? 'bg-cyber-primary/20 border-cyber-primary text-cyber-primary' : 'bg-cyber-danger/20 border-cyber-danger text-cyber-danger shadow-glow-danger'} font-mono text-2xl font-bold uppercase tracking-widest mb-2`}>
                  {result.result.attack_type}
                </div>
                <div className="flex items-center gap-2 mb-6 text-xs">
                  <span className="text-cyber-muted">Confidence: {(result.result.confidence * 100).toFixed(1)}%</span>
                  <span className={`px-2 py-0.5 rounded-full font-bold uppercase text-[10px] ${
                    result.result.confidence_level === 'High' ? 'bg-cyber-primary/20 text-cyber-primary' : 
                    result.result.confidence_level === 'Medium' ? 'bg-cyber-warning/20 text-cyber-warning' : 
                    'bg-cyber-danger/20 text-cyber-danger'
                  }`}>
                    {result.result.confidence_level}
                  </span>
                </div>
                
                {result.result.attack_type !== 'normal' && (
                  <button 
                    onClick={async () => {
                      try {
                        const btn = document.activeElement;
                        btn.disabled = true;
                        btn.innerText = "Generating Analysis...";
                        
                        const res = await axios.post(`${import.meta.env.VITE_API_URL}/api/explain`, {
                          prediction: result.result.attack_type,
                          features: JSON.parse(singleInput)
                        });
                        
                        window.dispatchEvent(new CustomEvent('open-ai-explanation', {
                          detail: {
                            content: res.data.explanation,
                            title: `THREAT_REPORT: ${result.result.attack_type.toUpperCase()}`
                          }
                        }));
                      } catch (err) {
                        alert("Error generating explanation.");
                      } finally {
                        const btn = document.querySelector('.explain-btn');
                        if (btn) {
                          btn.disabled = false;
                          btn.innerText = "EXPLAIN WITH AI";
                        }
                      }
                    }}
                    className="explain-btn px-6 py-2 bg-cyber-primary/10 hover:bg-cyber-primary/20 text-cyber-primary border border-cyber-primary/50 rounded-lg font-bold flex items-center gap-2 transition-all"
                  >
                    <Bot size={18} /> EXPLAIN WITH AI
                  </button>
                )}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
