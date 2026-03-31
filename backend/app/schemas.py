from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SinglePredictionRequest(BaseModel):
    features: Dict[str, Any]

class PredictionResult(BaseModel):
    attack_type: str
    confidence: float
    confidence_level: str
    is_low_confidence: bool

class BulkPredictionResponse(BaseModel):
    status: str = "success"
    total_records: int
    attacks_detected: int
    normal_traffic: int
    attack_percentage: float
    most_common_attack: str
    attack_distribution: Dict[str, int]
    average_confidence: float
    low_confidence_percentage: float
    risk_level: str

class SinglePredictionResponse(BaseModel):
    status: str
    result: PredictionResult

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    required_features: Optional[List[str]] = None
