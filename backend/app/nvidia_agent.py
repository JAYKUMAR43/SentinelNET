from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_with_agent(request: ChatRequest):
    api_key = os.getenv("NVIDIA_API_KEY")
    if api_key:
        api_key = api_key.strip()
        
    if not api_key:
        return {"error": "NVIDIA API Key is missing. Please configure your .env file."}
        
    try:
        # Initialize NVIDIA NIM Client (OpenAI compatible)
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
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
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            error_msg = "Invalid NVIDIA API Key. Please check your .env file."
        raise HTTPException(status_code=500, detail=f"AI Agent error: {error_msg}")
