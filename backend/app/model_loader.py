import os
import joblib

# Paths relative to the backend workspace
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "sentinel_pipeline.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "model", "features.pkl")

# We will cache the loaded models in memory
model = None
feature_columns = None

def load_models():
    """Loads the sentinel pipeline and the feature list into memory."""
    global model, feature_columns
    
    try:
        model = joblib.load(MODEL_PATH)
        print(f"Loaded model successfully from {MODEL_PATH}")
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        model = None
        
    try:
        feature_columns = joblib.load(FEATURES_PATH)
        print(f"Loaded features successfully from {FEATURES_PATH}")
    except Exception as e:
        print(f"Error loading features: {str(e)}")
        feature_columns = None

# Ensure models are loaded when the module is imported
load_models()

def get_model():
    return model

def get_feature_columns():
    return feature_columns