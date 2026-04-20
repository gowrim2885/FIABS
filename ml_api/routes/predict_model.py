from fastapi import APIRouter
import pandas as pd
import joblib
import os

router = APIRouter(prefix="/predict_model", tags=["predict_model"])

@router.get("/")
def predict():
    processed_data_path = "data/uploads/processed_data.csv"
    model_path = "models/gdp_model.pkl"

    if not os.path.exists(processed_data_path):
        return {"error": "Processed data not found. Please upload and process a dataset first."}
    
    if not os.path.exists(model_path):
        return {"error": "Model not trained. Please train the model first."}

    df = pd.read_csv(processed_data_path)
    model = joblib.load(model_path)

    # Use the latest available data point for prediction
    latest = df.iloc[-1]
    X = [[latest["revenue"], latest["inflation"]]]

    pred = model.predict(X)[0]

    return {
        "predicted_gdp": float(pred),
        "insight": "GDP is expected to grow if revenue increases and inflation is controlled."
    }
