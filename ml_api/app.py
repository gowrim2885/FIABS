from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import sys
import subprocess
import joblib
import numpy as np
import torch
from pydantic import BaseModel

# Load model and scaler once
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from predict import predict_gdp, model, scaler # Import pre-loaded model/scaler from predict.py

# Import public routes
from routes import analyst, auth, insights, predict_model, public, public_chat
from services.dataset_loader import yearly_summary

# Load anomaly model
anomaly_model = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../model/anomaly_model.pkl"))

class InputData(BaseModel):
    gdp: float
    inflation: float
    population: float
    unemployment: float
    interest: float
    deficit: float
    revenue: float
    expenditure: float

from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount static files for the frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register public routes
app.include_router(public.router)
app.include_router(public_chat.router)
app.include_router(analyst.router)
app.include_router(insights.router)
app.include_router(predict_model.router)
app.include_router(auth.router)

# Helper function to get latest data for dummy prediction
def get_latest_data():
    df = yearly_summary()
    latest_row = df.iloc[-1]
    
    # Internal feature list to match the model's scaler (8 features)
    features = ["gdp", "inflation", "population", "unemployment", "interest_rate", "fiscal_deficit", "revenue", "expenditure"]
    
    # Mapping for fallback keys if the exact name isn't found
    fallback = {
        "interest_rate": "interest",
        "fiscal_deficit": "deficit"
    }
    
    result = []
    for f in features:
        val = latest_row.get(f)
        if val is None and f in fallback:
            val = latest_row.get(fallback[f], 0.0)
        elif val is None:
            val = 0.0
        result.append(float(val))
        
    return result

def validate_input(data: InputData):
    """Full version input validation to prevent invalid data from reaching the model."""
    if data.gdp < 0:
        raise HTTPException(status_code=400, detail="GDP cannot be negative")
    if data.inflation < 0:
        raise HTTPException(status_code=400, detail="Inflation cannot be negative")
    if data.population <= 0:
        raise HTTPException(status_code=400, detail="Population must be greater than 0")
    if data.unemployment < 0:
        raise HTTPException(status_code=400, detail="Unemployment cannot be negative")
    if data.revenue < 0 or data.expenditure < 0:
        raise HTTPException(status_code=400, detail="Revenue/Expenditure cannot be negative")

@app.post("/predict")
async def predict(data: InputData):
    try:
        # 1. Validate Input
        validate_input(data)

        # 2. Prepare feature array
        input_data = np.array([[
            data.gdp,
            data.inflation,
            data.population,
            data.unemployment,
            data.interest,
            data.deficit,
            data.revenue,
            data.expenditure
        ]])

        # 3. Scale input
        input_scaled = scaler.transform(input_data)
        
        # 4. Convert to Tensor (samples, time_steps, features)
        input_tensor = torch.tensor(input_scaled, dtype=torch.float32).unsqueeze(1)
        
        # 5. Predict (get scaled output)
        with torch.no_grad():
            prediction_scaled = model(input_tensor).detach().numpy()
            
        # 6. Inverse Transform (Reconstruct full shape before inverse transform)
        # Using concatenation ensures we map correctly back to the GDP column
        prediction_actual = scaler.inverse_transform(
            np.concatenate([prediction_scaled, input_scaled[:, 1:]], axis=1)
        )[:, 0]

        predicted_gdp = float(prediction_actual[0])

        # 7. Multi-Year Prediction (5 Years Recursive)
        future_predictions = []
        current_input = input_scaled.copy()
        
        # Start year for predictions
        start_year = 2024
        
        for year_offset in range(1, 6):
            # 1. Predict next step
            temp_tensor = torch.tensor(current_input, dtype=torch.float32).unsqueeze(1)
            with torch.no_grad():
                pred_scaled = model(temp_tensor).detach().numpy()
            
            # 2. Inverse Transform
            full_row = np.concatenate([pred_scaled, current_input[:, 1:]], axis=1)
            actual_val = scaler.inverse_transform(full_row)[:, 0][0]
            
            future_predictions.append({
                "year": start_year + year_offset,
                "gdp": float(actual_val)
            })
            
            # 3. Update input for next recursive step (replace GDP with prediction)
            current_input[0, 0] = pred_scaled[0, 0]

        # 8. Anomaly Check
        anomaly_result = anomaly_model.predict(input_data)
        if anomaly_result[0] == -1:
            anomaly_status = "⚠️ Abnormal Spending Detected"
        else:
            anomaly_status = "Normal"

        # 8. Risk Simulation (Monte Carlo)
        simulations = []
        base_gdp = predicted_gdp
        for _ in range(100):
            # Simulate uncertainty with random inflation variance
            random_inflation = np.random.normal(data.inflation, 2)
            simulated_gdp = base_gdp * (1 + random_inflation / 100)
            simulations.append(simulated_gdp)
        
        risk_analysis = {
            "min_gdp": float(np.min(simulations)),
            "max_gdp": float(np.max(simulations)),
            "avg_gdp": float(np.mean(simulations))
        }

        # 9. Explainable AI (Factors)
        factors = []
        if data.inflation > 6:
            factors.append("High inflation")
        if data.deficit > 6:
            factors.append("High fiscal deficit")
        if data.revenue > data.expenditure:
            factors.append("Strong revenue performance")
        if not factors:
            factors.append("Balanced economic indicators")
        
        explanation = {
            "top_factors": factors,
            "reason": "GDP prediction influenced by key economic indicators"
        }

        # 10. Better Insight Logic
        if predicted_gdp > data.gdp:
            insight = "GDP is expected to grow due to higher revenue and controlled inflation 📈"
        else:
            insight = "GDP may decline due to fiscal imbalance and high deficit 📉"

        return {
            "status": "success",
            "predicted_gdp": predicted_gdp,
            "insight": insight,
            "anomaly": anomaly_status,
            "risk_analysis": risk_analysis,
            "explanation": explanation,
            "future_predictions": future_predictions
        }

    except HTTPException as he:
        # Re-raise HTTP exceptions from validation
        raise he
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/historical")
async def historical():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dataset_path = os.path.join(base_dir, "../data/processed/final_dataset.csv")
        df = pd.read_csv(dataset_path)
        df.columns = [c.strip().lower() for c in df.columns]
        historical_data = df[["year", "gdp"]].to_dict(orient="records")
        return {"status": "success", "historical_data": historical_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/allocate")
async def allocate_resources(data: dict):
    """Resource allocation module using Multi-Criteria Decision Making (MCDM)."""
    try:
        departments = data.get("departments", [])
        results = []
        for dept in departments:
            roi = dept.get("roi", 0)
            impact = dept.get("impact", 0)
            risk = dept.get("risk", 0)
            # Scoring logic: 40% ROI, 30% Impact, -30% Risk
            score = 0.4 * roi + 0.3 * impact - 0.3 * risk
            results.append({
                "name": dept.get("name", "Unknown"),
                "score": round(score, 2)
            })
        # Sort descending by score
        ranked = sorted(results, key=lambda x: x["score"], reverse=True)
        return {
            "status": "success",
            "ranking": ranked
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("Starting FIABS ML API Service (FastAPI) on Port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
