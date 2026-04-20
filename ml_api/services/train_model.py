import pandas as pd 
from sklearn.linear_model import LinearRegression 
import joblib 
import os

MODEL_PATH = "models/gdp_model.pkl" 
DATA_PATH = "data/uploads/processed_data.csv"

def train_model(): 
    if not os.path.exists(DATA_PATH):
        return "Error: Processed data not found. Please upload a dataset first."

    df = pd.read_csv(DATA_PATH) 

    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)

    # ML Path uses aggregated features
    X = df[["revenue", "inflation"]] 
    y = df["gdp"] 

    model = LinearRegression() 
    model.fit(X, y) 

    joblib.dump(model, MODEL_PATH) 

    return "Model trained successfully" 
