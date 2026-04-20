import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os

RAW_DATA_PATH = "data/uploads/raw_data.csv"

def predict_future_budget():
    """Predicts next year's budget for each department based on historical trends."""
    if not os.path.exists(RAW_DATA_PATH):
        return {"error": "Dataset not found for prediction."}

    df = pd.read_csv(RAW_DATA_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Standardize if needed
    if "actual_spending" in df.columns:
        df = df.rename(columns={"actual_spending": "expenditure", "total_budget": "revenue", "inflation_rate": "inflation"})

    latest_year = df["year"].max()
    next_year = latest_year + 1
    departments = df["department"].unique()
    
    predictions = []

    for dept in departments:
        dept_data = df[df["department"] == dept].sort_values("year")
        historical_years = dept_data["year"].tolist()
        historical_budgets = (dept_data["revenue"] if "revenue" in dept_data.columns else dept_data["budget"]).tolist()
        
        if len(dept_data) < 2:
            latest_budget = historical_budgets[-1]
            pred_budget = latest_budget * 1.05
        else:
            X = dept_data["year"].values.reshape(-1, 1)
            y = dept_data["revenue"].values if "revenue" in dept_data.columns else dept_data["budget"].values
            model = LinearRegression().fit(X, y)
            pred_budget = model.predict([[next_year]])[0]
            pred_budget = max(pred_budget, y[-1] * 1.02)

        predictions.append({
            "department": dept,
            "current_year": int(latest_year),
            "forecast_year": int(next_year),
            "predicted_budget": float(pred_budget),
            "growth_rate": float(((pred_budget / historical_budgets[-1]) - 1) * 100),
            "historical": {
                "years": historical_years,
                "values": historical_budgets
            }
        })

    return {
        "forecast_year": int(next_year),
        "predictions": predictions
    }
