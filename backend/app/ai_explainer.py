import os
import sys
import time
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

# Try to import Gemini API (new google-genai package)
try:
    from google import genai
    GEMINI_NEW_AVAILABLE = True
except ImportError:
    GEMINI_NEW_AVAILABLE = False

# Try to import older Gemini API (google-generativeai package)
try:
    import google.generativeai as google_genai_old
    GEMINI_OLD_AVAILABLE = True
except ImportError:
    GEMINI_OLD_AVAILABLE = False

# Try to import NVIDIA API (openai package)
try:
    from openai import OpenAI
    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False


def generate_local_explanation(prediction: str, features: Dict) -> str:
    """Generates immediate high-quality simulated threat reports as a local fallback."""
    feature_summary = "\n".join([f"* **{k}**: {v}" for k, v in features.items() if v != 0])
    pred_lower = prediction.lower()
    
    if "dos" in pred_lower or "ddos" in pred_lower:
        return f"""### 🛡️ Sentinel AI Threat Analysis: Denial of Service (DoS / DDoS)

#### 1. Threat Overview
A Denial of Service (**{prediction}**) attack attempts to make server resources or network bandwidth unavailable to legitimate users. Attackers achieve this by flooding the target system with an overwhelming volume of packet requests.

#### 2. Pattern Analysis
The system flagged this traffic as anomalous due to the following features:
{feature_summary if feature_summary else "* Pattern consistent with rapid resource consumption (SYN flood)."}

#### 3. Risk Assessment
* **Risk Level:** **HIGH**
* **Impact:** Interrupted network operations, service degradation, and gateway connection saturation.

#### 4. Immediate Mitigation Action Items
1. **Apply Rate Limiting:** Establish dynamic firewall limits to drop connections exceeding 100 requests/sec from single IPs.
2. **Configure Syn-Cookies:** Activate TCP SYN-cookies on server endpoints to shield resources during host sweeps.
3. **Scrub Perimeter Traffic:** Redirect incoming traffic flows to a third-party DDoS mitigation scrubbing proxy."""

    elif "scan" in pred_lower or "probe" in pred_lower or "nmap" in pred_lower:
        return f"""### 🛡️ Sentinel AI Threat Analysis: Network Reconnaissance (Port Scan)

#### 1. Threat Overview
Reconnaissance probing (**{prediction}**) is a technique where an attacker scans the network to discover online nodes, exposed ports, and active operating services to find vulnerabilities to exploit.

#### 2. Pattern Analysis
The system flagged this traffic as anomalous due to the following features:
{feature_summary if feature_summary else "* Sequential polling of multiple ports in rapid succession."}

#### 3. Risk Assessment
* **Risk Level:** **MEDIUM**
* **Impact:** Exposure of active port mappings, allowing targeted subsequent exploits of exposed legacy software.

#### 4. Immediate Mitigation Action Items
1. **Firewall Drop Rules:** Set IP filter policies to DROP scanning traffic rather than returning REJECT responses.
2. **Deploy Port Knocking:** Obfuscate administrative consoles (e.g. SSH, RDP) using standard port-knocking protocols.
3. **Disable Unused Ports:** Shutdown any unnecessary listening servers currently running on host nodes."""

    elif "brute" in pred_lower or "login" in pred_lower or "passwd" in pred_lower:
        return f"""### 🛡️ Sentinel AI Threat Analysis: Brute Force Authentication

#### 1. Threat Overview
Brute force (**{prediction}**) is an automated credential-guessing attack aiming to gain unauthorized access to server consoles by trying thousands of password combinations.

#### 2. Pattern Analysis
The system flagged this traffic as anomalous due to the following features:
{feature_summary if feature_summary else "* Repetitive authentication failures on system access portals."}

#### 3. Risk Assessment
* **Risk Level:** **HIGH**
* **Impact:** Administrative account compromise, lateral network movement, and full node takeover.

#### 4. Immediate Mitigation Action Items
1. **Host Lockouts:** Enable strict lockouts (e.g. `Fail2Ban`) to block IPs after 5 failed login attempts.
2. **Enforce Multi-Factor Auth:** Require MFA for all remote logons and SSH keys.
3. **Disable Password Logins:** Permit remote logins only via high-strength cryptographic keys."""

    else:
        return f"""### 🛡️ Sentinel AI Threat Analysis: Anomalous Activity ({prediction})

#### 1. Threat Overview
The traffic signature matching (**{prediction}**) shows deviations from regular baseline network traffic, representing potential intrusion vectors, malicious exploits, or lateral movements.

#### 2. Pattern Analysis
The system flagged this traffic as anomalous due to the following features:
{feature_summary if feature_summary else "* Unusual protocol flags or payloads."}

#### 3. Risk Assessment
* **Risk Level:** **MEDIUM**
* **Impact:** Anomaly signals possible active exploit testing or internal policy violations.

#### 4. Immediate Mitigation Action Items
1. **Isolate Source Node:** Quarantine the source IP from the main network zone.
2. **Inspect Packet Payload:** Perform full deep packet inspection on subsequent traffic from this origin.
3. **Review Access Logs:** Audit authentication and system log entries on the affected node."""


async def explain_threat_gemini(prediction: str, features: Dict) -> str:
    """Generate a detailed AI explanation using Google Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        api_key = api_key.strip()
        
    if not api_key:
        return "GEMINI_API_KEY is missing."
    
    if prediction.lower() == "normal":
        return "This traffic appears to be legitimate network activity with no malicious signatures detected."

    # Prepare feature summary
    feature_summary = ", ".join([f"{k}: {v}" for k, v in features.items() if v != 0])
    prompt = f"""You are Sentinel, a Cybersecurity Specialist.
The Network Intrusion Detection System has flagged an incoming packet as: **{prediction}**.

**Packet Context (Features):**
{feature_summary}

Please provide a detailed, scrollable explanation in Markdown including:
1. **Threat Overview:** What is {prediction} and how does it work?
2. **Analysis:** Why do these specific features indicate such an attack?
3. **Risk Level:** High/Medium/Low and the potential impact.
4. **Action Items:** 3 clear steps for the admin to mitigate or investigate this.

Format the output clearly with headers and bullet points."""

    # 1. Try new google-genai library if available
    if GEMINI_NEW_AVAILABLE:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini GenAI Error: {str(e)}")

    # 2. Try older google-generativeai library if available
    if GEMINI_OLD_AVAILABLE:
        try:
            google_genai_old.configure(api_key=api_key)
            # Try 1.5 Flash first, then fall back to pro
            for model_name in ["gemini-1.5-flash", "gemini-pro"]:
                try:
                    model = google_genai_old.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    return response.text
                except Exception as inner:
                    print(f"Older Gemini model {model_name} failed: {str(inner)}")
        except Exception as e:
            print(f"Older Gemini Error: {str(e)}")

    return "Gemini API failed or model not available."


async def explain_threat_nvidia(prediction: str, features: Dict) -> str:
    """Generate a detailed AI explanation using NVIDIA NIM API."""
    if not NVIDIA_AVAILABLE:
        return "OpenAI library not installed (required for NVIDIA NIM)."
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if api_key:
        api_key = api_key.strip()
        
    if not api_key:
        return "NVIDIA_API_KEY is missing."
    
    if prediction.lower() == "normal":
        return "This traffic appears to be legitimate network activity with no malicious signatures detected."

    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
            timeout=10.0
        )
        
        feature_summary = ", ".join([f"{k}: {v}" for k, v in features.items() if v != 0])
        prompt = f"""You are Sentinel, a Cybersecurity Specialist.
The Network Intrusion Detection System has flagged an incoming packet as: **{prediction}**.

**Packet Context (Features):**
{feature_summary}

Please provide a detailed, scrollable explanation in Markdown including:
1. **Threat Overview:** What is {prediction} and how does it work?
2. **Analysis:** Why do these specific features indicate such an attack?
3. **Risk Level:** High/Medium/Low and the potential impact.
4. **Action Items:** 3 clear steps for the admin to mitigate or investigate this.

Format the output clearly with headers and bullet points."""
        
        response = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": "You are a highly technical Cybersecurity Specialist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating AI explanation via NVIDIA: {str(e)}"


async def explain_threat(prediction: str, features: Dict) -> str:
    """
    Generate a detailed AI explanation for a given network traffic prediction.
    Tries NVIDIA first (known working), then falls back to Gemini, and then local expert templates.
    """
    if prediction.lower() == "normal":
        return "This traffic appears to be legitimate network activity with no malicious signatures detected."

    ai_provider = os.getenv("AI_PROVIDER", "auto").lower()
    
    # Try NVIDIA first since we verified it works in this environment
    if ai_provider == "nvidia" or ai_provider == "auto":
        if NVIDIA_AVAILABLE:
            result = await explain_threat_nvidia(prediction, features)
            if "Error" not in result and "missing" not in result:
                return result
        
        # Try Gemini next as backup
        result = await explain_threat_gemini(prediction, features)
        if "failed" not in result.lower() and "missing" not in result.lower():
            return result
            
    elif ai_provider == "gemini":
        result = await explain_threat_gemini(prediction, features)
        if "failed" not in result.lower() and "missing" not in result.lower():
            return result
            
        # Fallback to NVIDIA
        if NVIDIA_AVAILABLE:
            result = await explain_threat_nvidia(prediction, features)
            if "Error" not in result and "missing" not in result:
                return result

    # Standard ultimate local template fallback (instant, professional, reliable)
    return generate_local_explanation(prediction, features)
