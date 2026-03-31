from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any, Union
import pandas as pd
import numpy as np
import io
import logging
import time
from datetime import datetime
from collections import Counter
from fastapi.responses import JSONResponse
from app.model_loader import get_model, get_feature_columns
from app.state import state
from app.schemas import (
    SinglePredictionRequest, 
    BulkPredictionResponse, 
    SinglePredictionResponse, 
    PredictionResult,
    ErrorResponse
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# NSL-KDD Label Mapping
LABEL_MAP = {
    0: 'Normal',
    1: 'DoS',
    2: 'Probe',
    3: 'R2L',
    4: 'U2R'
}

def validate_input(df: pd.DataFrame) -> None:
    """Logs incoming columns and checks for basic data integrity."""
    logger.info(f"Incoming columns: {df.columns.tolist()}")
    if df.empty:
        raise ValueError("The provided data is empty.")

def preprocess_data(df: pd.DataFrame, expected_features: List[str]) -> pd.DataFrame:
    """
    Standardizes input data to match the model's expected feature set.
    Handles categorical encoding, missing columns, and reordering.
    """
    # 1. Normalize input column names (lowercase, strip whitespace)
    df.columns = [c.strip().lower() for c in df.columns]
    
    # 2. Categorical Mapping (protocol_type, service, flag)
    # The model expects one-hot encoded columns like 'protocol_type_tcp', 'service_http', etc.
    cat_cols = ['protocol_type', 'service', 'flag']
    
    # Create a copy to avoid SettingWithCopyWarning
    df_processed = df.copy()
    
    # Identify which expected features are one-hot encoded versions of these categories
    new_cols = {}
    for cat in cat_cols:
        if cat in df_processed.columns:
            prefix = f"{cat}_"
            for val in df_processed[cat].unique():
                one_hot_name = f"{prefix}{str(val).lower()}"
                # If this specific one-hot column is expected by the model, create it
                if one_hot_name in expected_features:
                    new_cols[one_hot_name] = (df_processed[cat].astype(str).str.lower() == str(val).lower()).astype(int)
    
    # 3. Align with expected features
    # Fill missing columns with 0, drop extras, and ensure order
    aligned_data = {}
    missing_features = []
    
    for feat in expected_features:
        feat_lower = feat.lower()
        if feat in df_processed.columns:
            aligned_data[feat] = df_processed[feat]
        elif feat_lower in df_processed.columns:
            aligned_data[feat] = df_processed[feat_lower]
        elif feat in new_cols:
            aligned_data[feat] = new_cols[feat]
        else:
            aligned_data[feat] = 0
            missing_features.append(feat)
    
    if missing_features:
        logger.warning(f"Missing features filled with 0: {missing_features}")
    
    # Create final DataFrame in correct order
    X = pd.DataFrame(aligned_data, index=df_processed.index)
    
    # Ensure all columns are numeric
    X = X.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    return X[expected_features]

def predict_with_confidence(model: Any, X: pd.DataFrame) -> List[PredictionResult]:
    """Makes predictions and assigns confidence levels (High/Medium/Low)."""
    try:
        raw_predictions = model.predict(X)
        
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X)
            
            # 1. Robust NaN Handling
            if np.isnan(probs).any():
                logger.warning("NaN detected in probabilities")
                probs = np.where(np.isnan(probs), 1e-6, probs)
            
            # 2. Shape Validation
            if len(probs.shape) != 2:
                raise ValueError(f"Invalid probability shape from model: {probs.shape}")
                
            # 3. Debug Instrumentation
            logger.info(f"Predictions check: {raw_predictions[:5]}")
            
            max_probs = np.max(probs, axis=1)
        else:
            max_probs = np.array([1.0] * len(raw_predictions))
        
        # Final safety check for max_probs
        max_probs = np.where(np.isnan(max_probs), 0.0, max_probs)
        
        results = []
        for pred, conf in zip(raw_predictions, max_probs):
            # 4. Safer Label Mapping
            try:
                pred_int = int(pred)
                attack_label = LABEL_MAP.get(pred_int, "Unknown")
            except Exception:
                attack_label = str(pred)
            
            # Confidence Level Classification
            if conf > 0.7:
                conf_level = "High"
            elif conf > 0.4:
                conf_level = "Medium"
            else:
                conf_level = "Low"
            
            results.append(PredictionResult(
                attack_type=attack_label,
                confidence=float(conf),
                confidence_level=conf_level,
                is_low_confidence=conf < 0.4
            ))
        
        return results
    except Exception as e:
        logger.error(f"Prediction logic error: {str(e)}")
        raise e

def generate_report(results: List[PredictionResult]) -> BulkPredictionResponse:
    """Generates a summary report matching the strict Phase 4 response format."""
    total_records = len(results)
    if total_records == 0:
        return BulkPredictionResponse(
            status="success",
            total_records=0,
            attacks_detected=0,
            normal_traffic=0,
            attack_percentage=0.0,
            most_common_attack="None",
            attack_distribution={},
            average_confidence=0.0,
            low_confidence_percentage=0.0,
            risk_level="Low"
        )
        
    attack_types = [r.attack_type for r in results if r.attack_type.lower() != 'normal']
    attacks_detected = len(attack_types)
    normal_traffic = total_records - attacks_detected
    attack_percentage = float((attacks_detected / total_records) * 100)
    
    # Robust Confidence Metrics
    confidences = [r.confidence for r in results]
    avg_confidence = float(np.mean(confidences))
    # Replace NaN if np.mean returns it (shouldn't happen with np.nan_to_num above)
    if np.isnan(avg_confidence):
        avg_confidence = 0.0
        
    low_conf_count = len([r for r in results if r.confidence < 0.4])
    low_conf_perc = float((low_conf_count / total_records) * 100)
    
    # Attack Distribution
    all_labels = [r.attack_type for r in results]
    dist_counter = Counter(all_labels)
    
    # Risk Level - Made flexible and same for all
    risk_level = "Medium"  # Consistent risk level regardless of threat presence
            
    return BulkPredictionResponse(
        status="success",
        total_records=total_records,
        attacks_detected=attacks_detected,
        normal_traffic=normal_traffic,
        attack_percentage=round(attack_percentage, 2),
        most_common_attack=Counter(attack_types).most_common(1)[0][0] if attack_types else "None",
        attack_distribution=dict(dist_counter),
        average_confidence=round(avg_confidence, 4),
        low_confidence_percentage=round(low_conf_perc, 2),
        risk_level=risk_level
    )

@router.post("/predict/bulk", response_model=Union[BulkPredictionResponse, ErrorResponse])
def predict_bulk(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(status="error", message="Only CSV files are allowed.").dict()
        )
    
    try:
        content = file.file.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
        validate_input(df)
    except Exception as e:
        logger.error(f"Error reading/validating CSV: {str(e)}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(status="error", message=f"Invalid CSV format: {str(e)}").dict()
        )

    model = get_model()
    features = get_feature_columns()

    if model is None or features is None:
        raise HTTPException(status_code=500, detail="Machine Learning model not loaded properly.")

    try:
        X = preprocess_data(df, features)
        results = predict_with_confidence(model, X)
        report = generate_report(results)
        
        # Update global state (for dashboard charts)
        all_labels = [r.attack_type for r in results]
        state.update_stats(report.total_records, report.attacks_detected, all_labels)
        
        # Log recent intrusions from bulk upload to history (limit to 5 to not flood)
        intrusions = [r for r in results if r.attack_type.lower() != 'normal'][:5]
        for intr in intrusions:
            state.add_to_log(intr.attack_type, "Bulk Analysis", "CSV", intr.confidence)
        
        return report
    except Exception as e:
        logger.error(f"Internal processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post("/predict/single", response_model=Union[SinglePredictionResponse, ErrorResponse])
def predict_single(request: SinglePredictionRequest):
    model = get_model()
    features = get_feature_columns()

    if model is None or features is None:
        raise HTTPException(status_code=500, detail="Machine Learning model not loaded properly.")
    
    try:
        df = pd.DataFrame([request.features])
        validate_input(df)
        X = preprocess_data(df, features)
        results = predict_with_confidence(model, X)
        result = results[0]
        
        # Update global state
        is_attack = result.attack_type.lower() != 'normal'
        state.update_stats(1, 1 if is_attack else 0, [result.attack_type])
        
        # Log to threat history
        state.add_to_log(result.attack_type, "Manual Input", "JSON", result.confidence)
        
        return SinglePredictionResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Single prediction error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(status="error", message=f"Prediction error: {str(e)}", required_features=features).dict()
        )