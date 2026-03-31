import time
from typing import List, Dict

class GlobalState:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.total_packets = 0
        self.attacks_detected = 0
        self.attack_distribution = {}
        self.attack_history = []
        self.threat_log = [] # Updated: store last 1000 events
        self._last_history_update = 0

    def add_to_log(self, prediction, source_ip="N/A", protocol="N/A", confidence=1.0):
        # New method to add individual threats to log
        timestamp = time.strftime("%H:%M:%S")
        self.threat_log.insert(0, {
            "timestamp": timestamp,
            "type": prediction,
            "source": source_ip,
            "protocol": protocol,
            "confidence": f"{confidence*100:.2f}%",
            "status": "Normal" if prediction.lower() == 'normal' else "Intrusion"
        })
        # Keep last 1000
        if len(self.threat_log) > 1000:
            self.threat_log.pop()

    def update_stats(self, total: int, attacks: int, labels: List[str]):
        from collections import Counter
        self.total_packets += total
        self.attacks_detected += attacks
        
        counts = Counter(labels)
        for t, count in counts.items():
            # Handle both 'normal' and translated 'Normal'
            if t.lower() != 'normal' and t != '0':
                self.attack_distribution[t] = self.attack_distribution.get(t, 0) + count
        
        # Update history
        current_time = int(time.time())
        # We group attacks by 10-second intervals for the graph
        interval = (current_time // 10) * 10
        
        if not self.attack_history or self.attack_history[-1]["time"] != interval:
            self.attack_history.append({"time": interval, "attacks": attacks})
        else:
            self.attack_history[-1]["attacks"] += attacks
            
        # Keep only the last 50 intervals to prevent memory leak
        if len(self.attack_history) > 50:
            self.attack_history.pop(0)

    def get_stats(self):
        # Calculate attack percentage
        percentage = (self.attacks_detected / self.total_packets * 100) if self.total_packets > 0 else 0
        
        # Determine most common attack
        most_common = "None"
        if self.attack_distribution:
            most_common = max(self.attack_distribution, key=self.attack_distribution.get)
            
        # Threat Frequency (1 threat per X packets)
        frequency = 0
        if self.attacks_detected > 0:
            frequency = round(self.total_packets / self.attacks_detected, 1)
            
        # Format distribution for Recharts
        dist_data = [{"name": k, "value": v} for k, v in self.attack_distribution.items()]
        # Add 'Normal' to distribution if not already handled or to show total
        normal_count = self.total_packets - self.attacks_detected
        # Ensure we don't have duplicate 'Normal' entries if it's already in distribution
        if not any(d['name'].lower() == 'normal' for d in dist_data):
            dist_data.insert(0, {"name": "Normal", "value": max(0, normal_count)})
            
        return {
            "total_scanned": self.total_packets,
            "attacks_detected": self.attacks_detected,
            "attack_percentage": percentage,
            "most_common_attack": most_common,
            "threat_frequency": f"1 per {frequency} pkts" if frequency > 0 else "N/A",
            "distribution": dist_data,
            "history": self.attack_history,
            "threat_log": self.threat_log # Include log in stats output
        }

# Singleton instance
state = GlobalState()
