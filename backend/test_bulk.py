import asyncio
import pandas as pd
import io
from app.predict import preprocess_features
from app.model_loader import get_model, get_feature_columns
import os

# Set working directory to backend
os.chdir(r"d:\SentinelNet-AI-Powered-Network-Intrusion-Detection-System-\backend")

async def test_bulk():
    csv_path = r"d:\SentinelNet-AI-Powered-Network-Intrusion-Detection-System-\week1 data\KDDTest.csv"
    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    model = get_model()
    features = get_feature_columns()
    
    if model is None or features is None:
        print("Model or features not loaded!")
        return

    print("Preprocessing...")
    try:
        X = preprocess_features(df, features)
        print(f"Input shape: {X.shape}")
        
        print("Predicting...")
        predictions = model.predict(X)
        print(f"Success! First 5 predictions: {predictions[:5]}")
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bulk())
