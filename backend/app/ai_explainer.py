from openai import OpenAI
import os
from typing import Dict

async def explain_threat(prediction: str, features: Dict) -> str:
    """
    Generate a detailed AI explanation for a given network traffic prediction using NVIDIA NIM.
    """
    api_key = os.getenv("NVIDIA_API_KEY")
    if api_key:
        api_key = api_key.strip()
        
    if not api_key:
        return "NVIDIA API Key is missing. Cannot provide AI explanation. Please configure your .env file."
    
    if prediction == "normal":
        return "This traffic appears to be legitimate network activity with no malicious signatures detected."

    try:
        # Initialize NVIDIA Client
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        
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

Format the output clearly with headers and bullet points.
"""
        
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
