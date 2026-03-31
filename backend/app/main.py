from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.predict import router as predict_router
from app.nvidia_agent import router as nvidia_router
from app.realtime import router as realtime_router
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(title="SentinelNet Network Intrusion Detection API")

# Setup CORS to allow React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
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

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": f"Internal Server Error: {str(exc)}"},
    )

@app.get("/")
def root():
    return {"message": "Welcome to SentinelNet AI-Powered NIDS"}