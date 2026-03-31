from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import random
import json
from app.state import state

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to Real-time Detection Socket")
    packet_buffer = []
    batch_size = 5  # Analyze every 5 packets
    try:
        while True:
            # Simulate real-time network traffic packet sniffing & inference
            await asyncio.sleep(random.uniform(0.5, 2.0)) # emit every 0.5-2.0 seconds
            
            # Generate packet data
            is_attack = random.random() < 0.15
            attack_types = ["Neptune (DoS)", "Smurf (DoS)", "Satan (Probe)", "PortsWeep (Probe)"]
            
            packet_data = {
                "source_ip": f"192.168.1.{random.randint(2, 254)}",
                "dest_ip": f"10.0.0.{random.randint(2, 254)}",
                "protocol": random.choice(["TCP", "UDP", "ICMP"]),
                "length": random.randint(40, 1500),
                "prediction": random.choice(attack_types) if is_attack else "normal",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            packet_buffer.append(packet_data)
            
            if len(packet_buffer) >= batch_size:
                # Analyze the batch
                batch_predictions = [p["prediction"] for p in packet_buffer]
                attacks_in_batch = [p for p in batch_predictions if p != "normal"]
                
                # Threat detection: if any attack in batch, mark as threat
                threat_detected = len(attacks_in_batch) > 0
                
                # Risk prediction: same for all, flexible
                risk_level = "Medium"  # Fixed risk level for consistency
                
                # Send batch data
                batch_data = {
                    "packets": packet_buffer,
                    "threat_detected": threat_detected,
                    "attacks_in_batch": attacks_in_batch,
                    "risk_level": risk_level,
                    "batch_timestamp": asyncio.get_event_loop().time()
                }
                
                # Update global state for the batch
                total_packets = len(packet_buffer)
                attacks_detected = len(attacks_in_batch)
                state.update_stats(total_packets, attacks_detected, batch_predictions)
                
                # Add to log for history
                for packet in packet_buffer:
                    if packet["prediction"] != "normal":
                        state.add_to_log(
                            packet["prediction"], 
                            packet["source_ip"], 
                            packet["protocol"]
                        )
                
                await websocket.send_text(json.dumps(batch_data))
                
                # Clear buffer
                packet_buffer = []
            
    except WebSocketDisconnect:
        print("Client disconnected from Real-time Detection Socket")
