import os
import sys
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

# Try to import Gemini API (new package)
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Try to import NVIDIA API
try:
    from openai import OpenAI
    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False


async def explain_threat_gemini(prediction: str, features: Dict) -> str:
    """
    Generate a detailed AI explanation using Google Gemini API (new google-genai package).
    """
    if not GEMINI_AVAILABLE:
        return "Google GenAI library not installed. Install with: pip install google-genai"
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        api_key = api_key.strip()
        
    if not api_key:
        return "GEMINI_API_KEY is missing. Cannot provide AI explanation. Please configure your .env file."
    
    if prediction == "normal":
        return "This traffic appears to be legitimate network activity with no malicious signatures detected."

    try:
        # Initialize Gemini with new package
        client = genai.Client(api_key=api_key)
        
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
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
        
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "Invalid" in error_msg or "403" in error_msg:
            return "Invalid GEMINI API Key. Please check your .env file."
        elif "429" in error_msg:
            return "Gemini API rate limit exceeded. Please try again later."
        else:
            return f"Error generating explanation via Gemini: {error_msg}"


async def explain_threat_nvidia(prediction: str, features: Dict) -> str:
    """
    Generate a detailed AI explanation using NVIDIA NIM API.
    """
    if not NVIDIA_AVAILABLE:
        return "OpenAI library not installed (required for NVIDIA NIM)."
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if api_key:
        api_key = api_key.strip()
        
    if not api_key:
        return "NVIDIA_API_KEY is missing. Cannot provide AI explanation. Please configure your .env file."
    
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
    Tries Gemini API first, falls back to NVIDIA NIM if needed.
    """
    ai_provider = os.getenv("AI_PROVIDER", "gemini").lower()
    
    if ai_provider == "gemini" or ai_provider == "auto":
        # Try Gemini first
        if GEMINI_AVAILABLE:
            result = await explain_threat_gemini(prediction, features)
            if "Error" not in result and "missing" not in result.lower():
                return result
        
        # Fall back to NVIDIA if Gemini failed
        if NVIDIA_AVAILABLE:
            return await explain_threat_nvidia(prediction, features)
        
        # No APIs available
        return "No AI explanation service available. Please configure GEMINI_API_KEY or NVIDIA_API_KEY in .env"
    
    elif ai_provider == "nvidia":
        return await explain_threat_nvidia(prediction, features)
    
    else:
        return "Invalid AI_PROVIDER setting. Use 'gemini' or 'nvidia'"



async def explain_threat_nvidia(prediction: str, features: Dict) -> str:
    """
    Generate a detailed AI explanation using NVIDIA NIM API.
    """
    if not NVIDIA_AVAILABLE:
        return "OpenAI library not installed (required for NVIDIA NIM)."
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if api_key:
        api_key = api_key.strip()
        
    if not api_key:
        return "NVIDIA_API_KEY is missing. Cannot provide AI explanation. Please configure your .env file."
    
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
    Tries Gemini API first, falls back to NVIDIA NIM if needed.
    """
    ai_provider = os.getenv("AI_PROVIDER", "gemini").lower()
    
    if ai_provider == "gemini" or ai_provider == "auto":
        # Try Gemini first
        if GEMINI_AVAILABLE:
            result = await explain_threat_gemini(prediction, features)
            if "Error" not in result and "missing" not in result.lower():
                return result
        
        # Fall back to NVIDIA if Gemini failed
        if NVIDIA_AVAILABLE:
            return await explain_threat_nvidia(prediction, features)
        
        # No APIs available
        return "No AI explanation service available. Please configure GEMINI_API_KEY or NVIDIA_API_KEY in .env"
    
    elif ai_provider == "nvidia":
        return await explain_threat_nvidia(prediction, features)
    
    else:
        return "Invalid AI_PROVIDER setting. Use 'gemini' or 'nvidia'"

