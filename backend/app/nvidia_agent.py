from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

def generate_simulated_response(message: str) -> str:
    """Generates immediate high-quality simulated security specialist answers if APIs fail or are slow."""
    msg = message.lower()
    
    if "ddos" in msg or "dos" in msg or "denial of service" in msg:
        return """### Simulated Security Intelligence (Backup Core)

**Threat Analysis: Denial of Service (DoS / DDoS)**
Denial of Service attacks aim to overwhelm a system's network bandwidth, CPU, or memory resources, rendering the services unavailable to legitimate users.

#### Key Indicators Detected:
* Extremely high volume of SYN packets (`SYN Flood`).
* Uniform packet sizes from spoofed origin IPs.
* Port exhaustion on gateway interfaces.

#### Immediate Action Items:
1. **Enable Rate Limiting:** Apply strict packet rate thresholds on the edge routers and firewalls.
2. **Deploy Traffic Scrubbing:** Route incoming traffic through a cloud scrub network (e.g. Cloudflare, AWS Shield) to filter out malicious packets.
3. **Configure Syn-Cookies:** Activate SYN cookies on servers to prevent state table exhaustion during SYN attacks."""

    elif "port scan" in msg or "nmap" in msg or "scan" in msg:
        return """### Simulated Security Intelligence (Backup Core)

**Threat Analysis: Port Scanning / Reconnaissance**
Reconnaissance traffic consists of probing multiple ports on a target node to identify open services, operating system versions, and potential vulnerabilities for exploitation.

#### Key Indicators Detected:
* Rapid scan probes across sequential TCP ports (`SYN scan`).
* Host sweeps scanning for online IP blocks.
* Unusual TCP flag combinations (e.g. NULL, FIN, or Xmas scans).

#### Immediate Action Items:
1. **Implement Firewall Dropping:** Configure host firewall rules (like `iptables` or Windows Firewall) to automatically DROP traffic from scanning IPs instead of returning a REJECT.
2. **Deploy Port Knocking:** Mask sensitive administrative ports (like SSH or RDP) using dynamic port knocking daemons.
3. **Close Unused Ports:** Audit active processes and disable any unnecessary ports or services currently exposed."""

    elif "brute force" in msg or "password" in msg or "ssh" in msg or "login" in msg:
        return """### Simulated Security Intelligence (Backup Core)

**Threat Analysis: Brute Force Authentication Attack**
Brute force attacks involve automated, repetitive attempts to guess user credentials (passwords, API keys) on exposed authentication systems.

#### Key Indicators Detected:
* Repeated failed authentication attempts on SSH (Port 22) or HTTP login panels.
* High dictionary-attack patterns using common username lists (`admin`, `root`).
* Parallel connection threads from multiple botnet nodes.

#### Immediate Action Items:
1. **Install Fail2Ban:** Install an active monitoring tool (like `Fail2ban` or `sshguard`) to automatically block IPs with more than 5 failed attempts.
2. **Enforce Multi-Factor Authentication (MFA):** Require MFA on all public-facing administrator interfaces.
3. **Disable Password Authentication:** For SSH, disable password logins entirely and enforce high-entropy SSH Key-based authentication."""

    elif "sql injection" in msg or "sqli" in msg or "database" in msg:
        return """### Simulated Security Intelligence (Backup Core)

**Threat Analysis: SQL Injection (SQLi)**
SQL Injection occurs when untrusted input is directly concatenated into SQL database queries, allowing attackers to read, modify, or delete backend databases.

#### Key Indicators Detected:
* Web request payloads containing database query patterns (`UNION SELECT`, `' OR 1=1 --`).
* Attempted database schema enumeration or admin table extraction.

#### Immediate Action Items:
1. **Implement Prepared Statements:** Rewrite database connection queries to use parameterized prepared statements exclusively.
2. **Deploy a Web Application Firewall (WAF):** Set up a WAF to scan and filter incoming HTTP POST/GET request payloads for SQL signatures.
3. **Apply Principle of Least Privilege:** Restrict database user accounts so they can only access specified tables, preventing full database compromise."""

    elif "mitigate" in msg or "prevent" in msg or "protect" in msg or "remediate" in msg:
        return """### Simulated Security Intelligence (Backup Core)

**Threat Mitigation Strategy Checklist**
To protect the perimeter of SentinelNet, you should execute a multi-layered security plan:

1. **Strict Firewall Configuration:** Adopt a "default-deny" firewall policy, only permitting explicitly whitelisted traffic.
2. **Continuous Vulnerability Patching:** Perform weekly automated scans and immediately patch CVE exploits on all network daemons.
3. **Intrusion Quarantine:** Ensure the NIDS is configured to automatically quarantine high-risk malicious IPs.
4. **Endpoint Auditing:** Regularly review authorization logs and enable detailed auditing across all critical nodes."""

    else:
        return """### Simulated Security Intelligence (Backup Core)

**Hello Admin. Sentinel NIDS Core is fully online.**
I have evaluated your request. As your automated AI analyst, here are standard recommendations to secure your infrastructure:

* **Active Monitoring:** Ensure that syslog streams from all network nodes are centralized and indexed for anomaly detection.
* **Network Segmentation:** Divide the network into isolated subnets (DMZ, Internal Server, User LAN) to contain potential breaches.
* **Traffic Inspection:** Monitor internal east-west traffic to identify potential lateral movement by attackers.

If you have specific threat logs (such as DDoS, Port Scanning, or Brute Force attempts), ask me directly for a customized risk overview and active mitigation steps!"""

@router.post("/chat")
async def chat_with_agent(request: ChatRequest):
    api_key = os.getenv("NVIDIA_API_KEY")
    if api_key:
        api_key = api_key.strip()
        
    if not api_key:
        reply = generate_simulated_response(request.message)
        return {"status": "success", "response": reply}
        
    try:
        # Initialize NVIDIA NIM Client (OpenAI compatible)
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
            timeout=10.0  # Safe timeout to prevent hanging
        )
        
        # Enhanced System Context
        system_prompt = """You are Sentinel, an advanced AI Security Analyst integrated into a Network Intrusion Detection System (NIDS). 
Your goal is to assist administrators by providing concise, accurate, and actionable security insights.
When responding:
1. Be professional and technical yet clear.
2. Use Markdown for formatting (bolding, lists, code blocks).
3. If asked about a specific threat from the system, explain its risk and give 2-3 immediate mitigation steps.
4. If you don't know something, suggest where the admin can find more info (e.g. CVE databases).
"""
        
        response = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
        )
        
        reply = response.choices[0].message.content
        return {"status": "success", "response": reply}
    except Exception as e:
        print(f"NVIDIA API Error: {str(e)}")
        # Fall back to simulated expert response in case of any timeout or failure
        reply = generate_simulated_response(request.message)
        return {"status": "success", "response": reply}
