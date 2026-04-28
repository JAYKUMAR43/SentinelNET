from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.predict import router as predict_router
from app.nvidia_agent import router as nvidia_router
from app.realtime import router as realtime_router
from app.config import validate_api_keys
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(title="SentinelNet Network Intrusion Detection API")

# Validate API Keys on startup
print("\n" + "="*50)
print("🚀 Initializing SentinelNet API Server")
print("="*50)
if validate_api_keys():
    print("✅ API Keys Configured Successfully")
else:
    print("❌ Warning: Some API Keys are not configured")
print("="*50 + "\n")

# Setup CORS to allow React Frontend
frontend_url = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.state import state
from app.ai_explainer import explain_threat

# Include routers
app.include_router(predict_router, prefix="/api", tags=["Predict"])
app.include_router(nvidia_router, prefix="/api/agent", tags=["AI Agent"])
app.include_router(realtime_router, prefix="/api/realtime", tags=["Real-time"])

@app.get("/api/stats")
async def get_stats():
    return state.get_stats()

@app.post("/api/explain")
async def explain(request: dict):
    prediction = request.get("prediction")
    features = request.get("features", {})
    explanation = await explain_threat(prediction, features)
    return {"explanation": explanation}

@app.post("/api/stats/reset")
async def reset_stats():
    state.reset()
    return {"status": "success", "message": "Statistics reset successfully"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint that validates API configurations."""
    from app.config import GEMINI_API_KEY, NVIDIA_API_KEY
    
    return {
        "status": "healthy",
        "app_name": "SentinelNet",
        "version": "1.0.0",
        "api_keys_configured": {
            "gemini": bool(GEMINI_API_KEY),
            "nvidia": bool(NVIDIA_API_KEY)
        }
    }

@app.post("/api/test-gemini")
async def test_gemini():
    """Test Google Gemini API connectivity and key validity."""
    from app.config import GEMINI_API_KEY
    
    if not GEMINI_API_KEY:
        return {
            "status": "error",
            "message": "GEMINI_API_KEY not configured in .env",
            "api_key_present": False
        }
    
    try:
        from google import genai
        
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Send a simple test prompt
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say 'Hello from SentinelNet'"
        )
        
        return {
            "status": "success",
            "message": "✅ Google Gemini API is working correctly!",
            "api_key_present": True,
            "api_response": response.text[:100],
            "model": "gemini-2.0-flash"
        }
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "Invalid" in error_msg or "403" in error_msg:
            return {
                "status": "error",
                "message": "❌ Invalid Google API Key",
                "error": error_msg,
                "api_key_present": True
            }
        else:
            return {
                "status": "error",
                "message": "❌ Error connecting to Gemini API",
                "error": error_msg,
                "api_key_present": True
            }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": f"Internal Server Error: {str(exc)}"},
    )

@app.get("/")
def root():
    return {"message": "Welcome to SentinelNet AI-Powered NIDS"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)